import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from datetime import datetime
import matplotlib as mpl
from typing import List
import matplotlib
from matplotlib import font_manager
import json


async def day_routes(pictures: List[str], info: str):
    """
    分解路径
    :param pictures: 图片存放路径
    :param info: 路径信息
    :return:
    """
    font_path = '/usr/share/fonts/truetype/SimHei.ttf'
    prop = font_manager.FontProperties(fname=font_path)

    # 设置字体
    plt.rcParams['font.family'] = prop.get_name()

    info_map = json.loads(info)
    data = info_map["datas"]

    # 设置图形大小，增加高度以适应所有图片
    fig, ax = plt.subplots(figsize=(3, 3 * len(data)))  # 高度根据图片数量动态调整
    fig.patch.set_facecolor('#FFE4E1')  # 使用更浅的粉色背景

    first = 3 * len(data) - 0.1 # 设置初始位置，确保从顶部开始

    for i in range(len(data)):
        img = mpimg.imread(pictures[i])  # 读取图片
        # 设置图片在坐标轴上的位置
        ax.imshow(img, extent=[0.1, 2.9, first - 1.8, first], zorder=1)
        names = data[i]["name"]
        times = data[i]["times"]
        left = 0.11
        for j in range(0, len(names)):
            circle = plt.Circle((left, first-1.8-0.1), 0.02, color='skyblue', fill=True, linewidth=2)
            ax.add_patch(circle)
            ax.text(left, first-1.8-0.1-0.05, names[j], rotation=270, fontsize=5, color='skyblue', ha='center', va='top')
            if j != len(names)-1:
                ax.plot([left, left+0.5], [first-1.8-0.1+0.02, first-1.8-0.1+0.02], color='skyblue', linewidth=1)
                ax.plot([left, left+0.5], [first-1.8-0.1-0.02, first-1.8-0.1-0.02], color='skyblue', linewidth=1)
                ax.text(left+0.25, first - 1.8 - 0.1 - 0.05, "{:.2f}".format(times[j])+"h", rotation=0, fontsize=5, color='skyblue', ha='center',
                        va='top')

            left += 0.5
        first -= 3  # 更新位置，确保图片不重叠

    ax.set_xlim(0, 3)
    ax.set_ylim(0, 3 * len(data))
    ax.axis('off')  # 关闭坐标轴
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    file_name = f"{timestamp}.png"
    file_path = "static/route/" + file_name
    plt.savefig("src/"+file_path, bbox_inches='tight', dpi=1500, pad_inches=0)
    plt.close()
    return file_path


if __name__ == "__main__":
    pictures_ = ["../static/route/1.png","../static/route/1.png", "../static/route/1.png"]
    info_ = """
    {
  "datas": [
    {
      "name": [
        "1906创意工厂",
        "三和老爷车博物馆",
        "三国茶园",
        "兰桂坊成都",
        "九眼桥"
      ],
      "times": [
        0.30972222222222223,
        0.3705555555555556,
        0.3591666666666667,
        0.18055555555555555
      ],
      "points": [
        {
          "latitude": 30.613708,
          "longitude": 104.083161
        },
        {
          "latitude": 30.597103,
          "longitude": 104.04128
        },
        {
          "latitude": 30.640942,
          "longitude": 104.042081
        },
        {
          "latitude": 30.643029,
          "longitude": 104.084482
        },
        {
          "latitude": 30.639417,
          "longitude": 104.088167
        }
      ],
      "ways": [
        1,
        1,
        1,
        0
      ],
      "id": [
        0,
        0,
        0,
        0,
        4
      ]
    },
    {
      "name": [
        "1906创意工厂",
        "三和老爷车博物馆",
        "三国茶园",
        "兰桂坊成都",
        "九眼桥"
      ],
      "times": [
        0.30972222222222223,
        0.3705555555555556,
        0.3591666666666667,
        0.18055555555555555
      ],
      "points": [
        {
          "latitude": 30.613708,
          "longitude": 104.083161
        },
        {
          "latitude": 30.597103,
          "longitude": 104.04128
        },
        {
          "latitude": 30.640942,
          "longitude": 104.042081
        },
        {
          "latitude": 30.643029,
          "longitude": 104.084482
        },
        {
          "latitude": 30.639417,
          "longitude": 104.088167
        }
      ],
      "ways": [
        1,
        1,
        1,
        0
      ],
      "id": [
        0,
        0,
        0,
        0,
        4
      ]
    },
    {
      "name": [
        "1906创意工厂",
        "三和老爷车博物馆",
        "三国茶园",
        "兰桂坊成都",
        "九眼桥"
      ],
      "times": [
        0.30972222222222223,
        0.3705555555555556,
        0.3591666666666667,
        0.18055555555555555
      ],
      "points": [
        {
          "latitude": 30.613708,
          "longitude": 104.083161
        },
        {
          "latitude": 30.597103,
          "longitude": 104.04128
        },
        {
          "latitude": 30.640942,
          "longitude": 104.042081
        },
        {
          "latitude": 30.643029,
          "longitude": 104.084482
        },
        {
          "latitude": 30.639417,
          "longitude": 104.088167
        }
      ],
      "ways": [
        1,
        1,
        1,
        0
      ],
      "id": [
        0,
        0,
        0,
        0,
        4
      ]
    }
  ]
}
"""
    day_routes(pictures_, info_)
