import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
from pyecharts.charts import WordCloud, Bar, Line, Pie, Scatter, Radar, Gauge
from pyecharts import options as opts
import pandas as pd
import streamlit.components.v1 as components

# 设置页面标题
st.title("文本分析与可视化工具")

# 文本输入框
url = st.text_input("请输入文章URL")

# 抓取文本内容
if url:
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        st.success("文本抓取成功！")
    except Exception as e:
        st.error(f"文本抓取失败: {e}")
        text = ""
else:
    text = ""

# 分词并统计词频
if text:
    words = jieba.lcut(text)
    word_counts = Counter(words)

    # 过滤掉长度为1的词
    filtered_word_counts = Counter({word: count for word, count in word_counts.items() if len(word) > 1})

    # 获取高频词
    top_20_words = filtered_word_counts.most_common(20)
    top_20_df = pd.DataFrame(top_20_words, columns=['词汇', '频次'])

    st.write("词频排名前20的词汇:")
    st.table(top_20_df)

    # 交互过滤低频词
    min_frequency = st.sidebar.slider("设置最低词频", min_value=1, max_value=max(filtered_word_counts.values()),
                                      value=1)
    filtered_word_counts = Counter(
        {word: count for word, count in filtered_word_counts.items() if count >= min_frequency})


    # 绘制词云
    def render_wordcloud():
        wc = WordCloud()
        wc.add("", list(filtered_word_counts.items()), word_size_range=[20, 100])
        return wc.render_embed()


    # 绘制柱状图
    def render_bar_chart():
        df = pd.DataFrame(list(filtered_word_counts.items()), columns=['词汇', '频次'])
        bar = Bar()
        bar.add_xaxis(df['词汇'].tolist())
        bar.add_yaxis("频次", df['频次'].tolist())
        return bar.render_embed()


    # 绘制折线图
    def render_line_chart():
        df = pd.DataFrame(list(filtered_word_counts.items()), columns=['词汇', '频次'])
        line = Line()
        line.add_xaxis(df['词汇'].tolist())
        line.add_yaxis("频次", df['频次'].tolist())
        return line.render_embed()


    # 绘制饼图
    def render_pie_chart():
        df = pd.DataFrame(list(filtered_word_counts.items()), columns=['词汇', '频次'])
        pie = Pie()
        pie.add("", [list(z) for z in zip(df['词汇'], df['频次'])])
        return pie.render_embed()


    # 绘制散点图
    def render_scatter_chart():
        df = pd.DataFrame(list(filtered_word_counts.items()), columns=['词汇', '频次'])
        scatter = Scatter()
        scatter.add_xaxis(df['词汇'].tolist())
        scatter.add_yaxis("频次", df['频次'].tolist())
        return scatter.render_embed()


    # 绘制雷达图
    def render_radar_chart():
        df = pd.DataFrame(list(filtered_word_counts.items()), columns=['词汇', '频次'])
        radar = Radar()
        indicator = [{"name": word, "max": max(filtered_word_counts.values())} for word in df['词汇']]
        radar.add_schema(schema=indicator)
        radar.add("频次", [list(df['频次'])], areastyle_opts=opts.AreaStyleOpts(opacity=0.1))
        return radar.render_embed()


    # 绘制仪表盘
    def render_gauge_chart():
        df = pd.DataFrame(list(filtered_word_counts.items()), columns=['词汇', '频次'])
        gauge = Gauge()
        gauge.add(
            "",
            [("频次", sum(df['频次']))],
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(
                    color=[[0.3, "#67e0e3"], [0.7, "#37a2da"], [1, "#fd666d"]]
                )
            )
        )
        return gauge.render_embed()


    # 侧边栏选择图表类型
    chart_type = st.sidebar.selectbox("选择图表类型",
                                      ["词云", "柱状图", "折线图", "饼图", "散点图", "雷达图", "仪表盘"])

    # 根据选择的图表类型渲染图表
    if chart_type == "词云":
        components.html(render_wordcloud(), height=600)
    elif chart_type == "柱状图":
        components.html(render_bar_chart(), height=600)
    elif chart_type == "折线图":
        components.html(render_line_chart(), height=600)
    elif chart_type == "饼图":
        components.html(render_pie_chart(), height=600)
    elif chart_type == "散点图":
        components.html(render_scatter_chart(), height=600)
    elif chart_type == "雷达图":
        components.html(render_radar_chart(), height=600)
    elif chart_type == "仪表盘":
        components.html(render_gauge_chart(), height=600)

# 运行Streamlit应用
# streamlit run app.py
