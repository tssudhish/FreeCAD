# SPDX-License-Identifier: LGPL-2.1-or-later

SET(AIAgent_SRCS
    __init__.py
    Init.py
    InitGui.py
    AIAgentCommand.py
    AIAgentPanel.py
    AIAgentMCPServer.py
)

SOURCE_GROUP("" FILES ${AIAgent_SRCS})

ADD_CUSTOM_TARGET(AIAgent ALL
    SOURCES ${AIAgent_SRCS}
)

fc_copy_sources(AIAgent "${CMAKE_BINARY_DIR}/Mod/AIAgent" ${AIAgent_SRCS})

INSTALL(
    FILES
        ${AIAgent_SRCS}
    DESTINATION Mod/AIAgent
)
