cmake_minimum_required(VERSION 3.20)
project(comicoftheday VERSION 1.0.0 LANGUAGES NONE)

install(FILES man/start-comicoftheday.1 man/stop-comicoftheday.1
        DESTINATION share/man/man1)

install(PROGRAMS start-comicoftheday.sh stop-comicoftheday.sh bootstrap.sh
        DESTINATION bin)

add_custom_target(bootstrap
    COMMAND ${CMAKE_SOURCE_DIR}/bootstrap.sh
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Setting up Python virtual environment"
)

add_custom_target(run
    COMMAND ${CMAKE_SOURCE_DIR}/start-comicoftheday.sh
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Starting Comic of the Day"
)
