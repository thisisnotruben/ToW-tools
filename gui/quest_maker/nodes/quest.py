from node_editor.node_node import Node
from quest_maker.calc_conf import *


@register_node(NODE_QUEST)
class QuestNode(Node):
    icon = "icons/in.png"
    op_code = NODE_QUEST
    op_title = "Quest"
    content_label_objname = "calc_node_quest"

    def __init__(self, scene, title='Quest Node', inputs=[], outputs=[]):
        super().__init__(scene, title=title, inputs=inputs, outputs=outputs)
        