"""
词云图生成器
"""
from wordcloud import WordCloud
from PIL import Image, ImageDraw
import numpy as np
import io
from collections import Counter


def create_circle_mask(width=800, height=600):
    """创建圆形遮罩 - 黑色区域是词云放置区域，白色区域是空白"""
    mask = Image.new('RGB', (width, height), 'white')  # 白色背景（不放词语）
    draw = ImageDraw.Draw(mask)
    # 绘制黑色椭圆（词云显示区域）- 占据90%的画布
    margin_x = int(width * 0.05)
    margin_y = int(height * 0.05)
    draw.ellipse([margin_x, margin_y, width-margin_x, height-margin_y], fill='black')
    return np.array(mask)


def create_cloud_mask(width=800, height=600):
    """创建云朵形状遮罩"""
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)

    # 绘制云朵形状（多个圆形组合）
    cx, cy = width // 2, height // 2
    draw.ellipse([cx-250, cy-100, cx+250, cy+100], fill=255)
    draw.ellipse([cx-200, cy-150, cx-50, cy+50], fill=255)
    draw.ellipse([cx+50, cy-150, cx+200, cy+50], fill=255)
    draw.ellipse([cx-150, cy-80, cx+150, cy+120], fill=255)

    return np.array(mask)


def generate_wordcloud_image(words_data, mask_type='circle', width=800, height=600):
    """
    生成词云图片

    Args:
        words_data: list of dict [{'skill': 'Python', 'count': 50}, ...]
        mask_type: 'circle' or 'cloud'
        width: 图片宽度
        height: 图片高度

    Returns:
        BytesIO: 图片字节流
    """
    # 准备词频数据
    word_freq = {item['skill']: item['count'] for item in words_data}

    # 创建遮罩
    if mask_type == 'cloud':
        mask = create_cloud_mask(width, height)
    else:
        mask = create_circle_mask(width, height)

    # 创建词云对象
    wc = WordCloud(
        font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',  # Linux字体路径
        mask=mask,
        width=width,
        height=height,
        background_color='white',
        max_words=50,
        relative_scaling=0.5,
        min_font_size=10,
        colormap='viridis',  # 使用viridis配色方案
        contour_width=2,
        contour_color='steelblue'
    ).generate_from_frequencies(word_freq)

    # 转换为图片
    image = wc.to_image()

    # 保存到字节流
    img_io = io.BytesIO()
    image.save(img_io, 'PNG', quality=95)
    img_io.seek(0)

    return img_io


def generate_colorful_wordcloud(words_data, width=800, height=600):
    """
    生成彩色渐变词云 - 紧密集中在中央的椭圆形，支持中英文
    """
    word_freq = {item['skill']: item['count'] for item in words_data}

    # 创建椭圆遮罩
    mask = create_circle_mask(width, height)

    # 自定义颜色函数 - 渐变色
    def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        # 根据字体大小返回不同颜色
        if font_size > 60:
            return f"hsl(220, 85%, 55%)"  # 深蓝色
        elif font_size > 45:
            return f"hsl(260, 80%, 60%)"  # 紫色
        elif font_size > 30:
            return f"hsl(300, 75%, 55%)"  # 品红色
        elif font_size > 20:
            return f"hsl(340, 80%, 60%)"  # 粉红色
        else:
            return f"hsl(180, 70%, 50%)"  # 青色

    # 尝试使用中文字体，如果不存在则使用默认字体
    import os
    chinese_fonts = [
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',  # 文泉驿正黑
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',  # 文泉驿微米黑
        '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',  # Droid Sans
        '/System/Library/Fonts/PingFang.ttc',  # macOS
        'C:\\Windows\\Fonts\\msyh.ttc',  # Windows 微软雅黑
    ]

    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'  # 默认
    for font in chinese_fonts:
        if os.path.exists(font):
            font_path = font
            break

    wc = WordCloud(
        font_path=font_path,  # 使用支持中文的字体
        mask=mask,
        width=width,
        height=height,
        background_color='white',
        mode='RGBA',
        max_words=50,
        relative_scaling=0.5,  # 降低相对缩放，让大小差异不那么大
        min_font_size=14,
        max_font_size=100,
        color_func=color_func,
        prefer_horizontal=0.8,  # 更多水平排列
        scale=2,  # 高清晰度
        margin=5,  # 边距
        random_state=42,  # 固定随机种子，保证布局一致
        collocations=False,  # 避免重复词组
    ).generate_from_frequencies(word_freq)

    image = wc.to_image()

    img_io = io.BytesIO()
    image.save(img_io, 'PNG', quality=95)
    img_io.seek(0)

    return img_io
