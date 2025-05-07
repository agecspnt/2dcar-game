# 2D赛车游戏

这是一个使用Python和Pygame开发的简单2D赛车游戏，全程使用**Cursor + Task-Master**完成。

## 项目描述

这个项目是一个基于Pygame库开发的2D赛车游戏，玩家可以控制一辆汽车在屏幕上移动，同时避开随机出现的障碍物。

## 功能特性

- 使用方向键控制汽车左右移动
- 随机生成的障碍物
- 碰撞检测系统
- 简洁的游戏界面
- 镜头跟随玩家汽车
- 使用来自 'Mini Pixel Pack 2' by GrafxKid 的像素艺术风格纹理

## 安装

1. 克隆项目:
   ```
   git clone https://github.com/agecspnt/2dcar-game.git
   cd 2dcar-game
   ```

2. 创建虚拟环境(可选):
   ```
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # 或
   .venv\Scripts\activate  # Windows
   ```

3. 安装依赖:
   ```
   pip install pygame
   ```

## 使用方法

运行主游戏:
```
python main.py
```

运行测试:
```
python test_pygame.py
```

## 控制

- `A` 键 - 向左移动汽车
- `D` 键 - 向右移动汽车
- 游戏结束时:
  - `R` 键 - 重新开始游戏
  - `Q` 键 - 退出游戏

## 项目进度

当前项目完成进度：100% (9/9任务)

### 已完成任务
1. ✅ **设置Python环境** - 为2D赛车游戏设置Python环境和必要的库
2. ✅ **加载游戏资源** - 加载赛车和障碍物图像
3. ✅ **设计游戏窗口** - 创建游戏窗口并初始化玩家汽车位置
4. ✅ **实现汽车移动** - 实现玩家汽车的连续向上移动和横向控制
5. ✅ **创建滚动环境** - 实现滚动背景或移动障碍物以模拟前进运动
6. ✅ **实现碰撞检测** - 检测玩家汽车与障碍物之间的碰撞
7. ✅ **实现相机跟随** - 确保游戏相机持续跟随玩家的汽车
8. ✅ **实现游戏结束状态** - 当发生碰撞时实现游戏结束状态，并提供重新开始/退出选项
9. ✅ **替换纹理资源** - 使用 'Mini Pixel Pack 2' 中的新纹理替换汽车和障碍物纹理，并处理精灵表。

### 待处理任务

## 素材来源

- 汽车和部分障碍物纹理来自 [Mini Pixel Pack 2 by GrafxKid on itch.io](https://grafxkid.itch.io/mini-pixel-pack-2) (Creative Commons Zero v1.0 Universal license)。

## 许可

这个项目使用MIT许可证 - 详见LICENSE文件。 