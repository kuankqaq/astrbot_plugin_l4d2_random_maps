import httpx
import random
import json
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("l4d2_random_map", "kuank", "随机抽取三方地图插件", "1.0.1", "https://github.com/kuankqaq/astrbot_plugin_l4d2_random_maps")
class RandomMapsPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("随机三方")
    async def random_maps(self, event: AstrMessageEvent, count: int = 1):
        """
        随机抽取指定数量的三方地图信息。

        Args:
            count (int): 抽取地图个数（默认1）
        """
        if count <= 0:
            yield event.plain_result("个数必须大于0，例如：/随机三方 3")
            return

        api_url = "https://maps.kuank.top/maomaps.json"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(api_url, timeout=10)
                response.raise_for_status()
                data = response.json()

            # 假设 JSON 是地图数组
            if not isinstance(data, list) or not data:
                yield event.plain_result("JSON 数据无效或为空，无法抽取地图。")
                return

            # 随机抽取（不超过总个数）
            actual_count = min(count, len(data))
            selected_maps = random.sample(data, actual_count)

            # 构建输出消息
            output = f"随机抽取了 {actual_count} 张地图：\n\n"
            for i, map_item in enumerate(selected_maps, 1):
                output += f"地图 {i}:\n"
                output += f"名称: {map_item.get('name', '未知')}\n"

                if map_item.get('steamUrl'):
                    output += f"工坊地址: {map_item['steamUrl']}\n"
                if map_item.get('downloadUrl'):
                    output += f"下载地址: {map_item['downloadUrl']}\n"
                if map_item.get('description'):
                    output += f"介绍: {map_item['description']}\n"

                output += "\n"  # 分隔下一张地图

            yield event.plain_result(output.strip())

            logger.info(f"成功抽取 {actual_count} 张地图给用户 {event.get_sender_name()}")

        except httpx.RequestError as e:
            logger.error(f"请求地图 JSON 时出错: {e}")
            yield event.plain_result("网络错误，无法获取地图数据。")
        except json.JSONDecodeError as e:
            logger.error(f"解析 JSON 时出错: {e}")
            yield event.plain_result("地图数据格式无效。")
        except Exception as e:
            logger.error(f"处理随机地图时发生未知错误: {e}")
            yield event.plain_result("抽取地图时发生未知错误。")