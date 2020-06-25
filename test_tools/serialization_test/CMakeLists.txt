add_executable(serialization_test
  main.cc
)

# Serialization test uses internal headers from the rlclientlib target
target_include_directories(PRIVATE $<TARGET_PROPERTY:rlclientlib,INCLUDE_DIRECTORIES>)

target_link_libraries(serialization_test PRIVATE Boost::program_options rlclientlib)
