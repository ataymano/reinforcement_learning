add_executable(onnx-player
  player.cc
)

target_link_libraries(onnx-player PRIVATE rlclientlib rlclientlib-onnx)
