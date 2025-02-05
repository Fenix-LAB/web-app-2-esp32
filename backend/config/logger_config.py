import logging

# from logging.config import dictConfig

# LOGGING_CONFIG = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "default": {
#             "format": "%(levelname)s %(asctime)s - %(message)s",
#             "use_colors": None,
#         },
#     },
#     "handlers": {
#         "default": {
#             "formatter": "default",
#             "class": "logging.StreamHandler",
#         },
#     },
#     "loggers": {
#         "uvicorn": {
#             "handlers": ["default"],
#             "level": "INFO",
#         },
#         "uvicorn.error": {
#             "handlers": ["default"],
#             "level": "INFO",
#             "propagate": True,
#         },
#         "uvicorn.access": {
#             "handlers": ["default"],
#             "level": "INFO",
#             "propagate": False,
#         },
#         "app": {
#             "handlers": ["default"],
#             "level": "DEBUG",
#             "propagate": False,
#         },
#     },
# }

# dictConfig(LOGGING_CONFIG)
# logger = logging.getLogger("app")


logger = logging.getLogger("uvicorn.error")
