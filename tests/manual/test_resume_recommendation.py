"""
简历分析和推荐功能测试脚本
用于验证AI返回的简历分析、职位推荐和简历修改建议是否准确
"""

from _bootstrap import PROJECT_ROOT

import os
import json
from typing import Dict, Any, List
from io import BytesIO

# Django 设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
import django
django.setup()

from jobs.ai_analyzer import ResumeAnalyzer, JobRecommender, ConversationalJobAssistant
from jobs.models import Job


class ResumeRecommendationTester:
    """简历推荐测试器"""

    def __init__(self):
        self.analyzer = ResumeAnalyzer()
        self.recommender = JobRecommender()
        self.assistant = ConversationalJobAssistant()

        # 存储测试结果
        self.test_results = []

    def generate_test_questions(self, resume_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        基于简历分析结果生成测试问题

        Args:
            resume_analysis: 简历分析结果

        Returns:
            测试问题列表
        """
        questions = []

        skills = resume_analysis.get('skills', [])
        experience_years = resume_analysis.get('experience_years', 0)
        education = resume_analysis.get('education', '')
        desired_position = resume_analysis.get('desired_position', '')
        desired_salary = resume_analysis.get('desired_salary', '')

        # 1. 基础信息提取准确性测试
        questions.append({
            'category': '基础信息提取',
            'question': f'简历中提取的技能是否准确？提取到的技能: {", ".join(skills)}',
            'expected_type': 'list',
            'validation': lambda x: isinstance(x, list) and len(x) > 0
        })

        questions.append({
            'category': '基础信息提取',
            'question': f'工作年限是否合理？提取到: {experience_years}年',
            'expected_type': 'number',
            'validation': lambda x: isinstance(x, (int, float)) and x >= 0
        })

        # 2. 职位推荐相关性测试
        if skills:
            questions.append({
                'category': '职位推荐',
                'question': f'基于技能 {skills[0]} 推荐的职位是否匹配？',
                'test_action': 'recommend',
                'expected_skills': skills[:3]  # 期望推荐的职位包含前3个技能
            })

        # 3. 薪资合理性测试
        if desired_salary:
            questions.append({
                'category': '薪资建议',
                'question': f'期望薪资 {desired_salary} 是否合理？',
                'test_action': 'salary_check',
                'salary_range': desired_salary
            })

        # 4. 简历优化建议测试
        questions.append({
            'category': '简历优化',
            'question': '能否提供针对性的简历修改建议？',
            'test_action': 'resume_optimization',
            'resume_context': resume_analysis
        })

        # 5. 技能差距分析测试
        if desired_position:
            questions.append({
                'category': '技能差距',
                'question': f'对于期望职位 {desired_position}，当前技能有哪些不足？',
                'test_action': 'skill_gap_analysis',
                'target_position': desired_position,
                'current_skills': skills
            })

        # 6. 职业发展建议测试
        questions.append({
            'category': '职业发展',
            'question': f'基于{experience_years}年经验和{education}学历，有什么职业发展建议？',
            'test_action': 'career_advice',
            'experience': experience_years,
            'education': education
        })

        return questions

    def validate_job_recommendation(self,
                                     recommendation_text: str,
                                     resume_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证职位推荐的准确性

        Args:
            recommendation_text: AI推荐的职位文本
            resume_analysis: 简历分析结果

        Returns:
            验证结果
        """
        validation_results = {
            'passed': True,
            'issues': [],
            'metrics': {}
        }

        skills = resume_analysis.get('skills', [])

        # 检查1: 推荐文本是否包含技能关键词
        skills_mentioned = 0
        for skill in skills[:5]:  # 检查前5个主要技能
            if skill.lower() in recommendation_text.lower():
                skills_mentioned += 1

        skill_coverage = skills_mentioned / min(len(skills), 5) if skills else 0
        validation_results['metrics']['skill_coverage'] = skill_coverage

        if skill_coverage < 0.3:  # 至少30%的技能被提及
            validation_results['passed'] = False
            validation_results['issues'].append(
                f'推荐结果中技能覆盖率过低: {skill_coverage:.1%}，期望至少30%'
            )

        # 检查2: 推荐文本是否包含具体职位
        job_keywords = ['职位', '岗位', '工程师', '开发', '专员', 'engineer', 'developer']
        has_job_mention = any(keyword in recommendation_text.lower() for keyword in job_keywords)
        validation_results['metrics']['has_job_mention'] = has_job_mention

        if not has_job_mention:
            validation_results['passed'] = False
            validation_results['issues'].append('推荐结果中未明确提及具体职位')

        # 检查3: 推荐文本长度是否合理
        text_length = len(recommendation_text)
        validation_results['metrics']['text_length'] = text_length

        if text_length < 50:
            validation_results['passed'] = False
            validation_results['issues'].append(f'推荐文本过短: {text_length}字符，期望至少50字符')

        return validation_results

    def test_conversational_responses(self, resume_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        测试对话式响应

        Args:
            resume_analysis: 简历分析结果

        Returns:
            测试结果列表
        """
        test_cases = []

        # 测试场景1: 请求职位推荐
        test_cases.append({
            'query': '请根据我的简历推荐合适的职位',
            'expected_keywords': ['推荐', '职位', '适合'],
            'context': resume_analysis
        })

        # 测试场景2: 询问薪资建议
        test_cases.append({
            'query': '我的期望薪资是否合理？',
            'expected_keywords': ['薪资', '合理', '市场'],
            'context': resume_analysis
        })

        # 测试场景3: 请求简历修改建议
        test_cases.append({
            'query': '我的简历有哪些可以改进的地方？',
            'expected_keywords': ['简历', '建议', '优化', '改进'],
            'context': resume_analysis
        })

        # 测试场景4: 技能提升建议
        test_cases.append({
            'query': '我应该学习哪些新技能？',
            'expected_keywords': ['技能', '学习', '提升'],
            'context': resume_analysis
        })

        results = []
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'='*60}")
            print(f"测试场景 {i}: {test_case['query']}")
            print('='*60)

            try:
                # 创建新的助手实例以避免历史污染
                assistant = ConversationalJobAssistant()
                response = assistant.chat(test_case['query'], resume_context=test_case['context'])

                if response.get('success'):
                    ai_response = response.get('response', '')
                    print(f"\nAI回复:\n{ai_response}\n")

                    # 验证响应
                    keywords_found = []
                    keywords_missing = []
                    for keyword in test_case['expected_keywords']:
                        if keyword in ai_response:
                            keywords_found.append(keyword)
                        else:
                            keywords_missing.append(keyword)

                    keyword_coverage = len(keywords_found) / len(test_case['expected_keywords'])
                    passed = keyword_coverage >= 0.5  # 至少50%的关键词被覆盖

                    result = {
                        'test_case': i,
                        'query': test_case['query'],
                        'passed': passed,
                        'response_length': len(ai_response),
                        'keywords_found': keywords_found,
                        'keywords_missing': keywords_missing,
                        'keyword_coverage': keyword_coverage,
                        'response': ai_response[:200] + '...' if len(ai_response) > 200 else ai_response
                    }

                    if passed:
                        print(f"✓ 测试通过 (关键词覆盖率: {keyword_coverage:.1%})")
                    else:
                        print(f"✗ 测试失败 (关键词覆盖率: {keyword_coverage:.1%})")
                        print(f"  缺失关键词: {', '.join(keywords_missing)}")

                    results.append(result)
                else:
                    print(f"✗ AI响应失败: {response.get('error')}")
                    results.append({
                        'test_case': i,
                        'query': test_case['query'],
                        'passed': False,
                        'error': response.get('error')
                    })

            except Exception as e:
                print(f"✗ 测试异常: {str(e)}")
                results.append({
                    'test_case': i,
                    'query': test_case['query'],
                    'passed': False,
                    'error': str(e)
                })

        return results

    def run_full_test(self, resume_text: str = None, resume_file_path: str = None) -> Dict[str, Any]:
        """
        运行完整测试

        Args:
            resume_text: 简历文本（可选）
            resume_file_path: 简历文件路径（可选）

        Returns:
            完整测试报告
        """
        print("="*80)
        print("简历分析和推荐功能测试")
        print("="*80)

        # 1. 获取简历文本
        if resume_text:
            text = resume_text
        elif resume_file_path:
            with open(resume_file_path, 'rb') as f:
                content = f.read()
                text = self.analyzer.extract_text(content, resume_file_path)
        else:
            # 使用示例简历数据
            text = """
            姓名：张三
            联系方式：zhangsan@example.com

            教育背景：
            本科 | 计算机科学与技术 | 2018-2022

            工作经验：
            AI工程师 | 网翊科技 | 2022.07 - 至今
            - 主导企业知识库系统建设，使用RAG技术
            - 负责大模型微调和Prompt工程
            - 开发Python自动化工具，提升团队效率30%

            软件工程师 | 江苏绚星智慧科技 | 2021.03 - 2022.06
            - 使用Django和React开发全栈Web应用
            - 参与系统架构设计和数据库优化

            技能：
            - 编程语言：Python, TypeScript, JavaScript, Java
            - AI/ML：PyTorch, TensorFlow, LangChain, RAG, LLM, Prompt工程
            - Web开发：Django, SpringBoot, React, Node.js
            - 数据库：MySQL, PostgreSQL
            - 工具：Git, Docker, Linux

            期望职位：AI工程师、大模型应用开发工程师
            期望薪资：15000-25000元/月
            """

        print(f"\n简历文本长度: {len(text)} 字符\n")

        # 2. 分析简历
        print("步骤1: 分析简历...")
        print("-"*80)
        try:
            resume_analysis = self.analyzer.analyze_resume(text)
            print(f"✓ 简历分析完成")
            print(f"\n分析结果:")
            print(json.dumps(resume_analysis, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"✗ 简历分析失败: {str(e)}")
            return {'success': False, 'error': str(e)}

        # 3. 生成测试问题
        print(f"\n步骤2: 生成测试问题...")
        print("-"*80)
        test_questions = self.generate_test_questions(resume_analysis)
        print(f"✓ 生成了 {len(test_questions)} 个测试问题\n")

        for i, q in enumerate(test_questions, 1):
            print(f"{i}. [{q['category']}] {q['question']}")

        # 4. 测试职位推荐
        print(f"\n步骤3: 测试职位推荐...")
        print("-"*80)
        try:
            recommendation = self.recommender.recommend_jobs(resume_analysis)

            if recommendation.get('success'):
                recommendation_text = recommendation.get('recommendation', '')
                print(f"✓ 职位推荐生成成功\n")
                print(f"推荐结果:\n{recommendation_text}\n")

                # 验证推荐准确性
                validation = self.validate_job_recommendation(recommendation_text, resume_analysis)
                print(f"推荐验证结果:")
                print(f"  通过: {validation['passed']}")
                print(f"  指标: {json.dumps(validation['metrics'], ensure_ascii=False, indent=4)}")
                if validation['issues']:
                    print(f"  问题:")
                    for issue in validation['issues']:
                        print(f"    - {issue}")
            else:
                print(f"✗ 职位推荐失败: {recommendation.get('error')}")
                validation = {'passed': False, 'issues': ['推荐生成失败']}
        except Exception as e:
            print(f"✗ 职位推荐异常: {str(e)}")
            validation = {'passed': False, 'issues': [str(e)]}

        # 5. 测试对话式交互
        print(f"\n步骤4: 测试对话式交互...")
        print("-"*80)
        conversation_results = self.test_conversational_responses(resume_analysis)

        # 6. 生成测试报告
        print(f"\n{'='*80}")
        print("测试总结")
        print("="*80)

        total_tests = len(conversation_results)
        passed_tests = sum(1 for r in conversation_results if r.get('passed', False))

        report = {
            'success': True,
            'resume_analysis': resume_analysis,
            'recommendation_validation': validation,
            'conversation_tests': {
                'total': total_tests,
                'passed': passed_tests,
                'failed': total_tests - passed_tests,
                'pass_rate': passed_tests / total_tests if total_tests > 0 else 0,
                'details': conversation_results
            },
            'overall_passed': validation.get('passed', False) and (passed_tests / total_tests >= 0.7 if total_tests > 0 else False)
        }

        print(f"\n职位推荐验证: {'✓ 通过' if validation.get('passed') else '✗ 失败'}")
        print(f"对话测试: {passed_tests}/{total_tests} 通过 ({report['conversation_tests']['pass_rate']:.1%})")
        print(f"总体评估: {'✓ 通过' if report['overall_passed'] else '✗ 需要改进'}")

        return report

    def save_report(self, report: Dict[str, Any], filename: str = 'test_report.json'):
        """保存测试报告到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n测试报告已保存到: {filename}")


def main():
    """主函数"""
    tester = ResumeRecommendationTester()

    # 运行测试（使用默认示例简历）
    report = tester.run_full_test()

    # 保存报告
    tester.save_report(report, 'reports/resume_recommendation_test_report.json')

    print(f"\n{'='*80}")
    print("测试完成！")
    print("="*80)


if __name__ == '__main__':
    main()
