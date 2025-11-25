"""
AI文档分析服务模块
使用 LangChain 1.0 + Function Call 分析简历并推荐职位
支持对话式交互和多轮问答
集成网络搜索功能获取最新招聘信息
"""

import os
import json
from typing import List, Dict, Any, Optional
from io import BytesIO

import PyPDF2
import pdfplumber
from docx import Document
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 网络搜索相关
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
import time
import random

from .models import Job


class ResumeAnalyzer:
    """简历分析器"""

    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """
        初始化分析器

        Args:
            api_key: LLM API密钥，如果为None则从环境变量读取
            base_url: API基础URL，如果为None则从环境变量读取
            model: 使用的模型名称，如果为None则从环境变量读取
        """
        self.api_key = api_key or os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("未找到 LLM API Key，请设置环境变量 LLM_API_KEY 或 OPENAI_API_KEY")

        self.base_url = base_url or os.getenv("LLM_BASE_URL")
        self.model = model or os.getenv("LLM_MODEL") or "qwen-plus"

        # 构建 LLM 配置
        llm_config = {
            "model": self.model,
            "openai_api_key": self.api_key,
            "temperature": 0.3
        }

        # 如果提供了自定义 base_url，添加到配置中
        if self.base_url:
            llm_config["openai_api_base"] = self.base_url

        self.llm = ChatOpenAI(**llm_config)

    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """从PDF提取文本"""
        text = ""

        # 首先尝试使用 pdfplumber
        try:
            with pdfplumber.open(BytesIO(file_content)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"pdfplumber 解析失败: {e}, 尝试使用 PyPDF2")

        # 如果 pdfplumber 失败，使用 PyPDF2
        if not text:
            try:
                pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            except Exception as e:
                print(f"PyPDF2 解析也失败: {e}")

        return text.strip()

    def extract_text_from_docx(self, file_content: bytes) -> str:
        """从Word文档提取文本"""
        try:
            doc = Document(BytesIO(file_content))
            text = "\n".join([para.text for para in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise ValueError(f"无法解析Word文档: {str(e)}")

    def extract_text(self, file_content: bytes, filename: str) -> str:
        """
        根据文件类型提取文本

        Args:
            file_content: 文件内容（字节）
            filename: 文件名

        Returns:
            提取的文本内容
        """
        filename_lower = filename.lower()

        if filename_lower.endswith('.pdf'):
            return self.extract_text_from_pdf(file_content)
        elif filename_lower.endswith(('.docx', '.doc')):
            return self.extract_text_from_docx(file_content)
        elif filename_lower.endswith('.txt'):
            return file_content.decode('utf-8', errors='ignore')
        else:
            raise ValueError(f"不支持的文件类型: {filename}")

    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        使用LLM分析简历内容

        Args:
            resume_text: 简历文本内容

        Returns:
            分析结果，包含技能、经验、学历等信息
        """
        prompt = f"""
请分析以下简历内容，提取关键信息。请以JSON格式返回结果，包含以下字段：
- skills: 技能列表（数组）
- experience_years: 工作年限（数字，如果无法确定返回0）
- education: 学历水平（本科/硕士/博士/大专/高中及以下）
- desired_position: 期望职位（如果简历中提到）
- desired_salary: 期望薪资范围（格式：最小值-最大值，单位：元/月）
- work_experience: 工作经历摘要
- key_strengths: 核心优势（3-5个关键点）

简历内容：
{resume_text}

请直接返回JSON格式的结果，不要包含其他内容。
"""

        try:
            messages = [
                SystemMessage(content="你是一个专业的简历分析助手，擅长提取简历中的关键信息。"),
                HumanMessage(content=prompt)
            ]

            response = self.llm.invoke(messages)
            result_text = response.content

            # 尝试解析JSON
            # 有时候LLM会返回带markdown代码块的JSON，需要清理
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]

            analysis = json.loads(result_text.strip())
            return analysis

        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print(f"原始响应: {result_text}")
            # 返回一个基本结构
            return {
                "skills": [],
                "experience_years": 0,
                "education": "未知",
                "desired_position": "",
                "desired_salary": "",
                "work_experience": "",
                "key_strengths": [],
                "error": "解析失败，请检查简历格式"
            }
        except Exception as e:
            print(f"分析简历时出错: {e}")
            raise


class JobRecommender:
    """职位推荐器 - 使用 Function Call"""

    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """
        初始化推荐器

        Args:
            api_key: LLM API密钥
            base_url: API基础URL
            model: 使用的模型名称
        """
        self.api_key = api_key or os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("未找到 LLM API Key")

        self.base_url = base_url or os.getenv("LLM_BASE_URL")
        self.model = model or os.getenv("LLM_MODEL") or "qwen-plus"

        # 构建 LLM 配置
        llm_config = {
            "model": self.model,
            "openai_api_key": self.api_key,
            "temperature": 0.3
        }

        # 如果提供了自定义 base_url，添加到配置中
        if self.base_url:
            llm_config["openai_api_base"] = self.base_url

        self.llm = ChatOpenAI(**llm_config)

        # 定义工具
        self.tools = [self._create_search_jobs_tool()]

        # 创建Agent
        self.agent = self._create_agent()

    def _create_search_jobs_tool(self):
        """创建搜索职位的工具（Function Call）"""

        @tool
        def search_jobs(
            skills: List[str] = None,
            position_title: str = None,
            min_salary: int = None,
            max_salary: int = None,
            education: str = None,
            experience: str = None,
            limit: int = 10
        ) -> str:
            """
            搜索匹配的职位。建议只传入skills参数（1-2个核心技能），其他参数可以不传。

            重要：使用通用技能关键词搜索，例如：
            - AI/机器学习方向：使用 Python, PyTorch, TensorFlow, Scikit-learn
            - Web开发方向：使用 Python, Django, React, Node.js
            - 避免使用太专业的术语如 LLM, RAG, Prompt工程等

            Args:
                skills: 技能列表（建议只传1-2个核心技能）
                position_title: 职位名称关键词（可选）
                min_salary: 最低薪资（可选，不建议使用）
                max_salary: 最高薪资（可选，不建议使用）
                education: 学历要求（可选，不建议使用）
                experience: 经验要求（可选，不建议使用）
                limit: 返回结果数量限制

            Returns:
                匹配的职位列表（JSON字符串）
            """
            from django.db.models import Q

            # 技能映射：将专业术语映射到通用技能
            skill_mapping = {
                'LLM': ['Python', 'PyTorch', 'TensorFlow'],
                'RAG': ['Python', 'Django', 'FastAPI'],
                'Prompt工程': ['Python', 'PyTorch'],
                '大模型': ['Python', 'PyTorch', 'TensorFlow'],
                'AI': ['Python', 'PyTorch', 'TensorFlow'],
                '机器学习': ['Python', 'Scikit-learn', 'PyTorch'],
                '深度学习': ['PyTorch', 'TensorFlow', 'Keras'],
            }

            # 扩展技能列表
            expanded_skills = []
            if skills:
                for skill in skills:
                    expanded_skills.append(skill)
                    # 如果是专业术语，添加映射的通用技能
                    if skill in skill_mapping:
                        expanded_skills.extend(skill_mapping[skill])
                # 去重
                expanded_skills = list(set(expanded_skills))

            # 第一次尝试：使用扩展后的技能搜索
            queryset = Job.objects.filter(is_active=True)

            # 根据职位标题搜索
            if position_title:
                queryset = queryset.filter(title__icontains=position_title)

            # 根据技能搜索（OR关系）
            if expanded_skills:
                skill_query = Q()
                for skill in expanded_skills:
                    skill_query |= Q(tags__icontains=skill)
                queryset = queryset.filter(skill_query)

            # 薪资范围（放宽20%）
            if min_salary:
                queryset = queryset.filter(salary_max__gte=int(min_salary * 0.8))
            if max_salary:
                queryset = queryset.filter(salary_min__lte=int(max_salary * 1.2))

            # 学历（包含"不限"）
            if education:
                education_levels = {
                    "博士": ["博士", "不限"],
                    "硕士": ["博士", "硕士", "不限"],
                    "本科": ["博士", "硕士", "本科", "不限"],
                    "大专": ["博士", "硕士", "本科", "大专", "不限"],
                }
                allowed_educations = education_levels.get(education, ["不限"])
                queryset = queryset.filter(education__in=allowed_educations)

            jobs = queryset.select_related('company')[:limit]

            # 如果没有结果，逐步放宽条件
            if not jobs.exists() and expanded_skills:
                # 第二次尝试：只用技能搜索，忽略其他条件
                queryset = Job.objects.filter(is_active=True)
                skill_query = Q()
                for skill in expanded_skills:
                    skill_query |= Q(tags__icontains=skill)
                jobs = queryset.filter(skill_query)[:limit]

            # 第三次尝试：使用最通用的技能（Python）
            if not jobs.exists() and 'Python' in expanded_skills:
                jobs = Job.objects.filter(is_active=True, tags__icontains='Python')[:limit]

            # 最后兜底：返回算法工程师和数据分析师职位
            if not jobs.exists():
                jobs = Job.objects.filter(
                    is_active=True,
                    title__in=['算法工程师', '数据分析师', 'Python开发工程师', '后端开发工程师']
                )[:limit]

            # 转换为JSON格式
            results = []
            for job in jobs:
                results.append({
                    'id': job.id,
                    'title': job.title,
                    'company': job.company.name if job.company else '未知',
                    'salary_range': f"{job.salary_min}-{job.salary_max}元/月",
                    'city': job.city,
                    'education': job.education,
                    'experience': job.experience,
                    'skills': job.tags,
                    'description': job.description[:200] if job.description else '',
                })

            return json.dumps(results, ensure_ascii=False)

        return search_jobs

    def _create_agent(self):
        """创建 LangChain Agent（使用 Tool Calling）"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的职位推荐助手。根据用户的简历信息，使用提供的工具搜索最匹配的职位。

重要规则：
1. 只调用一次 search_jobs 工具，不要反复调用
2. 搜索时只使用1-2个**通用技能关键词**，不要使用太多条件
3. 不要设置薪资、学历、经验等限制条件，让工具自动匹配
4. 如果搜索返回结果，直接分析并推荐
5. 必须返回具体的职位列表，包括职位名称、公司、薪资等信息

搜索策略（非常重要）：
- 优先使用通用技能关键词：Python, Java, JavaScript, React, Django, Node.js等
- 如果用户简历提到AI/大模型，使用：Python, PyTorch, TensorFlow
- 如果用户简历提到Web开发，使用：Python, Django, React, Node.js
- 避免使用太专业的术语：不要用 LLM, RAG, Prompt工程 等搜索
- 使用 skills 参数传入1-2个通用技能即可

输出格式：
必须包含具体的职位列表，格式如下：
1. 【职位名称】（公司 | 薪资范围 | 城市）
   - 匹配原因：...
2. 【职位名称】（公司 | 薪资范围 | 城市）
   - 匹配原因：...

请以友好的方式总结推荐的职位，并说明推荐理由。"""),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=3,  # 限制最大迭代次数
            handle_parsing_errors=True
        )

        return agent_executor

    def recommend_jobs(self, resume_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于简历分析结果推荐职位

        Args:
            resume_analysis: 简历分析结果

        Returns:
            推荐结果，包含职位列表和推荐理由
        """
        # 构建输入提示
        input_text = f"""
请根据以下简历分析结果推荐合适的职位：

技能: {', '.join(resume_analysis.get('skills', []))}
工作年限: {resume_analysis.get('experience_years', 0)}年
学历: {resume_analysis.get('education', '未知')}
期望职位: {resume_analysis.get('desired_position', '不限')}
期望薪资: {resume_analysis.get('desired_salary', '不限')}
核心优势: {', '.join(resume_analysis.get('key_strengths', []))}

请为我推荐最匹配的职位。
"""

        try:
            # 使用Agent执行推荐
            result = self.agent.invoke({"input": input_text})

            return {
                "success": True,
                "recommendation": result.get("output", ""),
                "resume_analysis": resume_analysis
            }

        except Exception as e:
            print(f"推荐职位时出错: {e}")
            return {
                "success": False,
                "error": str(e),
                "resume_analysis": resume_analysis
            }


def analyze_and_recommend(file_content: bytes, filename: str) -> Dict[str, Any]:
    """
    完整的分析和推荐流程

    Args:
        file_content: 文件内容
        filename: 文件名

    Returns:
        包含简历分析和职位推荐的完整结果
    """
    try:
        # 1. 提取简历文本
        analyzer = ResumeAnalyzer()
        resume_text = analyzer.extract_text(file_content, filename)

        if not resume_text:
            return {
                "success": False,
                "error": "无法从文档中提取文本内容"
            }

        # 2. 分析简历
        analysis = analyzer.analyze_resume(resume_text)

        # 3. 推荐职位
        recommender = JobRecommender()
        recommendation = recommender.recommend_jobs(analysis)

        # 4. 添加原始简历文本到返回结果中
        if recommendation.get('success'):
            recommendation['resume_text'] = resume_text  # 添加原始文本
            recommendation['filename'] = filename  # 添加文件名

        return recommendation

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


class ConversationalJobAssistant:
    """
    对话式职位推荐助手
    支持多轮对话和交互式职位推荐
    """

    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """
        初始化对话助手

        Args:
            api_key: LLM API密钥
            base_url: API基础URL
            model: 使用的模型名称
        """
        self.api_key = api_key or os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("未找到 LLM API Key")

        self.base_url = base_url or os.getenv("LLM_BASE_URL")
        self.model = model or os.getenv("LLM_MODEL") or "qwen-plus"

        # 构建 LLM 配置
        llm_config = {
            "model": self.model,
            "openai_api_key": self.api_key,
            "temperature": 0.5
        }

        # 如果提供了自定义 base_url，添加到配置中
        if self.base_url:
            llm_config["openai_api_base"] = self.base_url

        self.llm = ChatOpenAI(**llm_config)

        # 对话历史
        self.conversation_history: List[Dict[str, str]] = []

        # 定义工具
        self.tools = self._create_tools()

        # 创建Agent
        self.agent = self._create_conversational_agent()

    def _create_tools(self):
        """创建工具集"""

        @tool
        def search_jobs_by_keywords(
            keywords: str,
            limit: int = 5
        ) -> str:
            """
            根据关键词搜索职位

            Args:
                keywords: 搜索关键词（可以是职位名称、技能等）
                limit: 返回结果数量

            Returns:
                匹配的职位列表（JSON字符串）
            """
            queryset = Job.objects.filter(is_active=True)
            queryset = queryset.filter(
                title__icontains=keywords
            ) | queryset.filter(
                tags__icontains=keywords
            )

            jobs = queryset.select_related('company')[:limit]
            results = []
            for job in jobs:
                results.append({
                    'id': job.id,
                    'title': job.title,
                    'company': job.company.name if job.company else '未知',
                    'salary_range': f"{job.salary_min}-{job.salary_max}元/月",
                    'city': job.city,
                    'education': job.education,
                    'experience': job.experience,
                    'skills': job.tags,
                    'description': job.description[:200] if job.description else '',
                })

            return json.dumps(results, ensure_ascii=False)

        @tool
        def search_jobs_advanced(
            skills: Optional[List[str]] = None,
            position_title: Optional[str] = None,
            min_salary: Optional[int] = None,
            max_salary: Optional[int] = None,
            city: Optional[str] = None,
            education: Optional[str] = None,
            experience: Optional[str] = None,
            limit: int = 5
        ) -> str:
            """
            高级职位搜索

            Args:
                skills: 技能列表
                position_title: 职位名称关键词
                min_salary: 最低薪资（月薪，单位：元）
                max_salary: 最高薪资（月薪，单位：元）
                city: 城市
                education: 学历要求
                experience: 经验要求
                limit: 返回结果数量

            Returns:
                匹配的职位列表（JSON字符串）
            """
            from django.db.models import Q

            queryset = Job.objects.filter(is_active=True)

            if position_title:
                queryset = queryset.filter(title__icontains=position_title)

            # 技能搜索改为OR关系
            if skills:
                skill_query = Q()
                for skill in skills:
                    skill_query |= Q(tags__icontains=skill)
                queryset = queryset.filter(skill_query)

            # 薪资范围放宽20%
            if min_salary:
                queryset = queryset.filter(salary_max__gte=int(min_salary * 0.8))
            if max_salary:
                queryset = queryset.filter(salary_min__lte=int(max_salary * 1.2))

            if city:
                queryset = queryset.filter(city__icontains=city)

            # 学历包含"不限"
            if education:
                education_levels = {
                    "博士": ["博士", "不限"],
                    "硕士": ["博士", "硕士", "不限"],
                    "本科": ["博士", "硕士", "本科", "不限"],
                    "大专": ["博士", "硕士", "本科", "大专", "不限"],
                }
                allowed_educations = education_levels.get(education, ["不限"])
                queryset = queryset.filter(education__in=allowed_educations)

            # 暂时不限制经验
            # if experience:
            #     queryset = queryset.filter(experience__icontains=experience)

            jobs = queryset.select_related('company')[:limit]
            results = []
            for job in jobs:
                results.append({
                    'id': job.id,
                    'title': job.title,
                    'company': job.company.name if job.company else '未知',
                    'salary_range': f"{job.salary_min}-{job.salary_max}元/月",
                    'city': job.city,
                    'education': job.education,
                    'experience': job.experience,
                    'skills': job.tags,
                    'description': job.description[:200] if job.description else '',
                })

            return json.dumps(results, ensure_ascii=False)

        @tool
        def get_job_details(job_id: int) -> str:
            """
            获取职位详细信息

            Args:
                job_id: 职位ID

            Returns:
                职位详细信息（JSON字符串）
            """
            try:
                job = Job.objects.select_related('company').get(id=job_id, is_active=True)
                result = {
                    'id': job.id,
                    'title': job.title,
                    'company': job.company.name if job.company else '未知',
                    'company_info': {
                        'industry': job.company.industry if job.company else '',
                        'company_type': job.company.company_type if job.company else '',
                        'company_size': job.company.company_size if job.company else '',
                    },
                    'salary_range': f"{job.salary_min}-{job.salary_max}元/月",
                    'city': job.city,
                    'education': job.education,
                    'experience': job.experience,
                    'skills': job.tags,
                    'description': job.description,
                    'requirements': job.requirements,
                    'welfare': job.welfare,
                }
                return json.dumps(result, ensure_ascii=False)
            except Job.DoesNotExist:
                return json.dumps({"error": "职位不存在"}, ensure_ascii=False)

        @tool
        def search_web_for_jobs(
            query: str,
            max_results: int = 5
        ) -> str:
            """
            在网上搜索最新的招聘信息

            Args:
                query: 搜索查询，例如"Python开发工程师 北京 2024"
                max_results: 返回结果数量

            Returns:
                搜索结果（JSON字符串）
            """
            try:
                # 添加招聘相关关键词
                search_query = f"{query} 招聘 最新"

                # 添加随机延迟避免速率限制
                time.sleep(random.uniform(1, 2))

                # 尝试搜索，添加重试机制
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        with DDGS() as ddgs:
                            results = list(ddgs.text(search_query, max_results=max_results))
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            time.sleep(random.uniform(2, 4))
                            continue
                        else:
                            raise e

                formatted_results = []
                for i, result in enumerate(results, 1):
                    formatted_results.append({
                        'rank': i,
                        'title': result.get('title', ''),
                        'snippet': result.get('body', ''),
                        'url': result.get('href', ''),
                    })

                return json.dumps({
                    'success': True,
                    'query': query,
                    'count': len(formatted_results),
                    'results': formatted_results
                }, ensure_ascii=False)
            except Exception as e:
                error_msg = str(e)
                # 如果是速率限制错误，提供友好的提示
                if 'Ratelimit' in error_msg or '202' in error_msg:
                    return json.dumps({
                        'success': False,
                        'error': '网络搜索暂时不可用（请求过于频繁），请稍后再试。建议先使用数据库搜索功能。'
                    }, ensure_ascii=False)
                return json.dumps({
                    'success': False,
                    'error': f'搜索失败: {error_msg}'
                }, ensure_ascii=False)

        @tool
        def search_salary_trends(
            position: str,
            city: str = None
        ) -> str:
            """
            搜索行业薪资趋势和市场行情

            Args:
                position: 职位名称，例如"Python开发工程师"
                city: 城市名称（可选），例如"北京"

            Returns:
                薪资趋势信息（JSON字符串）
            """
            try:
                # 构建搜索查询
                query = f"{position} 薪资 行情"
                if city:
                    query = f"{city} {query}"
                query += " 2024"

                # 添加随机延迟
                time.sleep(random.uniform(1, 2))

                # 尝试搜索，添加重试机制
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        with DDGS() as ddgs:
                            results = list(ddgs.text(query, max_results=3))
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            time.sleep(random.uniform(2, 4))
                            continue
                        else:
                            raise e

                formatted_results = []
                for result in results:
                    formatted_results.append({
                        'title': result.get('title', ''),
                        'snippet': result.get('body', ''),
                        'url': result.get('href', ''),
                    })

                return json.dumps({
                    'success': True,
                    'position': position,
                    'city': city or '全国',
                    'count': len(formatted_results),
                    'results': formatted_results
                }, ensure_ascii=False)
            except Exception as e:
                error_msg = str(e)
                if 'Ratelimit' in error_msg or '202' in error_msg:
                    return json.dumps({
                        'success': False,
                        'error': '网络搜索暂时不可用（请求过于频繁），请稍后再试。建议先查看数据库中的薪资数据。'
                    }, ensure_ascii=False)
                return json.dumps({
                    'success': False,
                    'error': f'搜索薪资信息失败: {error_msg}'
                }, ensure_ascii=False)

        @tool
        def search_company_info(
            company_name: str
        ) -> str:
            """
            搜索公司背景资料和评价

            Args:
                company_name: 公司名称

            Returns:
                公司信息（JSON字符串）
            """
            try:
                # 搜索公司信息
                query = f"{company_name} 公司 怎么样 评价"

                # 添加随机延迟
                time.sleep(random.uniform(1, 2))

                # 尝试搜索，添加重试机制
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        with DDGS() as ddgs:
                            results = list(ddgs.text(query, max_results=3))
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            time.sleep(random.uniform(2, 4))
                            continue
                        else:
                            raise e

                formatted_results = []
                for result in results:
                    formatted_results.append({
                        'title': result.get('title', ''),
                        'snippet': result.get('body', ''),
                        'url': result.get('href', ''),
                    })

                return json.dumps({
                    'success': True,
                    'company': company_name,
                    'count': len(formatted_results),
                    'results': formatted_results
                }, ensure_ascii=False)
            except Exception as e:
                error_msg = str(e)
                if 'Ratelimit' in error_msg or '202' in error_msg:
                    return json.dumps({
                        'success': False,
                        'error': '网络搜索暂时不可用（请求过于频繁），请稍后再试。'
                    }, ensure_ascii=False)
                return json.dumps({
                    'success': False,
                    'error': f'搜索公司信息失败: {error_msg}'
                }, ensure_ascii=False)

        return [
            search_jobs_by_keywords,
            search_jobs_advanced,
            get_job_details,
            search_web_for_jobs,
            search_salary_trends,
            search_company_info
        ]

    def _create_conversational_agent(self):
        """创建对话式Agent"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业友好的职位推荐助手。你可以帮助用户：
1. 分析他们的简历和职业背景
2. 根据他们的技能、经验和期望推荐合适的职位
3. 回答关于职位的各种问题
4. 提供职业发展建议
5. 获取最新的招聘信息和行业资讯

你有以下工具可以使用：

【数据库查询工具】
- search_jobs_by_keywords: 快速根据关键词搜索数据库中的职位
- search_jobs_advanced: 使用多个条件进行高级搜索（技能、薪资、城市等）
- get_job_details: 获取特定职位的详细信息

【网络搜索工具】
- search_web_for_jobs: 在网上搜索最新的招聘信息
- search_salary_trends: 搜索行业薪资趋势和市场行情
- search_company_info: 搜索公司背景资料和评价

使用建议：
1. 优先使用数据库工具查询本地职位数据（速度快、数据准确）
2. 当用户想了解最新招聘动态时，使用 search_web_for_jobs
3. 当用户询问薪资水平时，结合数据库数据和 search_salary_trends 给出建议
4. 当用户对某公司感兴趣时，使用 search_company_info 提供更多背景信息

请以友好、专业的方式与用户交流，理解他们的需求，并提供有价值的建议。"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5
        )

        return agent_executor

    def chat(self, user_message: str, resume_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        处理用户消息并返回响应

        Args:
            user_message: 用户消息
            resume_context: 简历分析上下文（可选）

        Returns:
            包含AI响应和更新后的对话历史
        """
        try:
            # 如果提供了简历上下文，在第一次对话时添加到消息中
            if resume_context and not self.conversation_history:
                context_message = f"""
我已经分析了您的简历，以下是关键信息：
- 技能: {', '.join(resume_context.get('skills', []))}
- 工作年限: {resume_context.get('experience_years', 0)}年
- 学历: {resume_context.get('education', '未知')}
- 期望职位: {resume_context.get('desired_position', '不限')}
- 期望薪资: {resume_context.get('desired_salary', '不限')}
- 核心优势: {', '.join(resume_context.get('key_strengths', []))}

现在让我为您推荐合适的职位。{user_message}
"""
                input_message = context_message
            else:
                input_message = user_message

            # 转换对话历史为LangChain消息格式
            chat_history = []
            for msg in self.conversation_history:
                if msg['role'] == 'user':
                    chat_history.append(HumanMessage(content=msg['content']))
                elif msg['role'] == 'assistant':
                    chat_history.append(AIMessage(content=msg['content']))

            # 执行Agent
            result = self.agent.invoke({
                "input": input_message,
                "chat_history": chat_history
            })

            ai_response = result.get("output", "抱歉，我无法处理您的请求。")

            # 更新对话历史
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_response
            })

            return {
                "success": True,
                "response": ai_response,
                "conversation_history": self.conversation_history
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": f"抱歉，处理您的消息时出现错误: {str(e)}"
            }

    def reset_conversation(self):
        """重置对话历史"""
        self.conversation_history = []


def create_conversational_session(resume_analysis: Optional[Dict[str, Any]] = None) -> ConversationalJobAssistant:
    """
    创建对话式会话

    Args:
        resume_analysis: 简历分析结果（可选）

    Returns:
        对话助手实例
    """
    assistant = ConversationalJobAssistant()
    return assistant


class ResumeOptimizer:
    """简历优化器 - 使用 AI 优化简历内容"""

    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """
        初始化优化器

        Args:
            api_key: LLM API密钥，如果为None则从环境变量读取
            base_url: API基础URL，如果为None则从环境变量读取
            model: 使用的模型名称，如果为None则从环境变量读取
        """
        self.api_key = api_key or os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("未找到 LLM API Key，请设置环境变量 LLM_API_KEY 或 OPENAI_API_KEY")

        self.base_url = base_url or os.getenv("LLM_BASE_URL")
        self.model = model or os.getenv("LLM_MODEL") or "qwen-plus"

        # 构建 LLM 配置
        llm_config = {
            "model": self.model,
            "openai_api_key": self.api_key,
            "temperature": 0.7  # 提高创造性
        }

        # 如果提供了自定义 base_url，添加到配置中
        if self.base_url:
            llm_config["openai_api_base"] = self.base_url

        self.llm = ChatOpenAI(**llm_config)

    def optimize_resume(
        self,
        resume_text: str,
        analysis_data: Dict[str, Any],
        target_position: str = None,
        optimization_goals: List[str] = None
    ) -> Dict[str, Any]:
        """
        优化简历内容

        Args:
            resume_text: 原始简历文本
            analysis_data: 简历分析数据
            target_position: 目标职位（可选）
            optimization_goals: 优化目标列表（可选）

        Returns:
            优化结果，包含优化后的内容和修改说明
        """
        # 默认优化目标
        if not optimization_goals:
            optimization_goals = [
                "量化工作成果，添加具体数据和指标",
                "突出与目标职位相关的技能和经验",
                "使用动作动词开头，增强表现力",
                "优化内容结构，突出核心优势",
                "精简冗余信息，提高简洁性"
            ]

        # 构建优化提示
        target_position_text = f"目标职位：{target_position}" if target_position else "通用职位优化"

        goals_text = "\n".join([f"{i+1}. {goal}" for i, goal in enumerate(optimization_goals)])

        prompt = f"""
你是一位专业的简历优化顾问，请帮助优化以下简历。

{target_position_text}

优化目标：
{goals_text}

当前简历分析结果：
- 技能：{', '.join(analysis_data.get('skills', []))}
- 工作年限：{analysis_data.get('experience_years', 0)} 年
- 学历：{analysis_data.get('education', '未知')}
- 核心优势：{', '.join(analysis_data.get('key_strengths', []))}

原始简历内容：
{resume_text}

请提供：
1. 优化后的完整简历（结构化JSON格式，包含以下部分）：
   - personal_info: {{name, phone, email, location}}
   - job_intent: {{position, salary, location}}
   - education: [{{school, major, degree, time, description}}]
   - skills: [分类技能组，如 {{"category": "编程语言", "items": ["Python", "Java"]}}] 或 简单列表
   - work_experience: [{{company, position, time, responsibilities: []}}]
   - projects: [{{name, time, description, tech_stack: [], achievements: []}}]
   - self_evaluation: 个人评价文本

2. 主要修改说明（列表形式）：
   - 每条说明包含：section（部分名称）、change_type（修改类型）、reason（原因）、example（具体示例）

请以如下JSON格式返回：
{{
  "optimized_resume": {{...完整的简历数据...}},
  "changes": [
    {{
      "section": "技能",
      "change_type": "量化增强",
      "reason": "添加具体的技能水平和使用时长",
      "example": "Python → Python (3年经验，熟练使用Django/Flask框架)"
    }},
    ...
  ],
  "optimization_summary": "整体优化说明"
}}

注意：
- 保持真实性，不要编造虚假信息
- 对于数据不足的部分，可以合理推断但要标注
- 确保JSON格式正确，可以被解析
"""

        try:
            messages = [
                SystemMessage(content="你是一位专业的简历优化顾问，擅长将普通简历改写为高质量的专业简历。"),
                HumanMessage(content=prompt)
            ]

            response = self.llm.invoke(messages)
            result_text = response.content

            # 解析JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]

            optimization_result = json.loads(result_text.strip())

            return {
                "success": True,
                "optimized_resume": optimization_result.get("optimized_resume", {}),
                "changes": optimization_result.get("changes", []),
                "optimization_summary": optimization_result.get("optimization_summary", ""),
                "original_analysis": analysis_data
            }

        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print(f"原始响应: {result_text}")
            return {
                "success": False,
                "error": "优化结果解析失败，AI 返回的格式不正确",
                "raw_response": result_text[:500]  # 只返回前500字符
            }
        except Exception as e:
            import traceback
            error_msg = str(e)
            print(f"优化简历时出错: {error_msg}")
            print(f"详细错误: {traceback.format_exc()}")

            # 根据错误类型返回更友好的提示
            if "Connection" in error_msg or "connection" in error_msg.lower():
                return {
                    "success": False,
                    "error": "网络连接失败，请检查网络连接或稍后重试"
                }
            elif "timeout" in error_msg.lower():
                return {
                    "success": False,
                    "error": "请求超时，请稍后重试"
                }
            elif "API" in error_msg or "key" in error_msg.lower():
                return {
                    "success": False,
                    "error": "API 配置错误，请检查 API Key 配置"
                }
            else:
                return {
                    "success": False,
                    "error": f"优化失败: {error_msg[:200]}"
                }

    def generate_improvement_suggestions(
        self,
        analysis_data: Dict[str, Any],
        target_position: str = None
    ) -> List[Dict[str, str]]:
        """
        生成简历改进建议（不进行完整重写）

        Args:
            analysis_data: 简历分析数据
            target_position: 目标职位（可选）

        Returns:
            改进建议列表
        """
        target_text = f"针对 {target_position} 职位" if target_position else ""

        prompt = f"""
请{target_text}为以下简历提供具体的改进建议。

简历分析结果：
- 技能：{', '.join(analysis_data.get('skills', []))}
- 工作年限：{analysis_data.get('experience_years', 0)} 年
- 学历：{analysis_data.get('education', '未知')}
- 期望职位：{analysis_data.get('desired_position', '未提及')}
- 核心优势：{', '.join(analysis_data.get('key_strengths', []))}
- 工作经历：{analysis_data.get('work_experience', '未提供')[:500]}

请提供5-8条具体的改进建议，每条建议包含：
1. section: 需要改进的部分（技能/经验/教育/其他）
2. suggestion: 具体建议
3. priority: 优先级（高/中/低）
4. example: 改进示例（如果适用）

请以JSON格式返回：
{{
  "suggestions": [
    {{
      "section": "技能",
      "suggestion": "建议量化技能水平",
      "priority": "高",
      "example": "Python → Python (3年，精通Django)"
    }},
    ...
  ]
}}
"""

        try:
            messages = [
                SystemMessage(content="你是一位专业的简历顾问，擅长给出实用的改进建议。"),
                HumanMessage(content=prompt)
            ]

            response = self.llm.invoke(messages)
            result_text = response.content

            # 解析JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]

            result = json.loads(result_text.strip())
            return result.get("suggestions", [])

        except Exception as e:
            print(f"生成建议时出错: {e}")
            return []
