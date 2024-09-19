from dataclasses import dataclass, field
from generate_nginx_conf import generate_nginx_config

class Language_Type:
    """
    supported language type
    
    """
    
    python_flask = "python_flask"
    react = "react"
    nextjs = "nextjs"
    nodejs = "nodejs"

class Deployment_Type:
    """
    supported deployment type
    
    """
    
    frontend = "frontend"
    backend = "backend"
    fullstack = "fullstack"

@dataclass
class Frontend_Base_Config:
    """
    Base config for frontend applications
    
    """
    type: str = None
    VERSION: str = None
    File_Name: str = None
    LANGUAGE_TYPE: str = None
    PORT: int = 80
    OUTPUT_DIR: str = "dist"
    INSTALL_COMMAND: str = "npm install"
    BUILD_COMMAND: str = "npm run build"
    RUN_COMMAND: list = field(default_factory=list)
    FRONTEND_PATH: str = "/"
    ENV_VARIABLES: dict = field(default_factory=dict)


@dataclass
class Backend_Base_Config:
    """
    Base config for backend applications
    
    """
    type: str = None
    VERSION: str = None
    File_Name: str = None
    LANGUAGE_TYPE: str = None
    PORT: int = 3000
    OUTPUT_DIR: str = None
    INSTALL_COMMAND: str = None
    BUILD_COMMAND: str = None
    RUN_COMMAND: list = field(default_factory=list)
    BACKEND_PATH: str = "/api/"
    ENV_VARIABLES: dict = field(default_factory=dict)


@dataclass
class Nginx_Conf:
    """
    Nginx configuration for generating nginx config file

    """
    language_type: str = None
    deployment_type: str = None
    frontend_path: str = "/"
    frontend_port: int = 3000
    frontend_ip: str = "localhost"
    backend_ip: str = "localhost"
    backend_path: str = "/api/"
    backend_port: int = 5000

@dataclass
class Fullstack_Deployment_Config:
    """
    Fullstack deployment config
    
    """
    nginx_configuration: str
    frontend_config: Frontend_Base_Config
    backend_config: Backend_Base_Config

@dataclass
class Frontend_Deployment_Config:
    """
    Frontend deployment config
    
    """
    nginx_configuration: str 
    frontend_config: Frontend_Base_Config

@dataclass
class Backend_Deployment_Config:
    """
    Backend deployment config
    
    """
    
    backend_config: Backend_Base_Config

# Adding Defaults attributes for each Language_Type
@dataclass
class Python_Flask_Lang(Backend_Base_Config):
    """
    Python Default Values
    
    """

    LANGUAGE_TYPE: str = Language_Type.python_flask
    PORT: int = 5000 
    RUN_COMMAND: list = field(default_factory=lambda: ["python_flask", "app.py"])

@dataclass
class NodeJS_Lang(Backend_Base_Config):
    """
    NodeJS Default Values

    """

    LANGUAGE_TYPE: str = Language_Type.nodejs
    PORT: int = 3000
    INSTALL_COMMAND: str = "npm install"
    RUN_COMMAND: list = field(default_factory=lambda: ["node", "app.js"])

@dataclass
class ReactLang(Frontend_Base_Config):
    """
    React Default Values
    
    """

    LANGUAGE_TYPE: str = Language_Type.react


@dataclass
class NextJSLang(Frontend_Base_Config):
    """
    NextJS Default Values

    """

    LANGUAGE_TYPE: str = Language_Type.nextjs
    VERSION: str = "lts"
    RUN_COMMAND: list = field(default_factory=lambda: ["npm", "run", "start"])
    BUILD_COMMAND: str = None
    INSTALL_COMMAND: str = "npm install"
    OUTPUT_DIR: str = ".next"
    PORT: int = 3000


def get_language_config(**lang_config):
    """
    Get language configuration based on language type
    
    """
    language_config_map = {
        Language_Type.python_flask: Python_Flask_Lang,
        Language_Type.react: ReactLang,
        Language_Type.nextjs: NextJSLang,
        Language_Type.nodejs: NodeJS_Lang,
    }
    language_type = lang_config.get("LANGUAGE_TYPE")
    language_class = language_config_map.get(language_type)
    if language_class:
        return language_class(**lang_config)
    else:
        raise ValueError(f"Unsupported language type: {language_type}")

def create_nginx_config(deployment_type, **lang_config):
    """
    Creating nginx configuration
    Here the language types are only of frontend

    """
    nginx_configuration={}
    if deployment_type == Deployment_Type.frontend:
        nginx_configuration["language_type"]=lang_config.get("LANGUAGE_TYPE")
        nginx_configuration["frontend_path"]=lang_config.get("FRONTEND_PATH","/")
        nginx_configuration["frontend_port"]=lang_config.get("PORT")
        nginx_configuration["deployment_type"]=deployment_type
        return generate_nginx_config(**vars(Nginx_Conf(**nginx_configuration)))
    
    elif deployment_type == Deployment_Type.fullstack:
        nginx_configuration["language_type"]=lang_config["frontend"].get("LANGUAGE_TYPE")
        nginx_configuration["frontend_path"]=lang_config["frontend"].get("FRONTEND_PATH", "/")
        nginx_configuration["frontend_port"]=lang_config["frontend"].get("PORT")
        nginx_configuration["deployment_type"]=deployment_type
        nginx_configuration["backend_path"]=lang_config["backend"].get("BACKEND_PATH", "/")
        nginx_configuration["backend_port"]=lang_config["backend"].get("PORT")
        return generate_nginx_config(**vars(Nginx_Conf(**nginx_configuration)))
    else:
        raise ValueError(f"Unsupported deployment type: {deployment_type}")

def create_deployment_config(deployment_type, lang_configs):
    """
    Creating deployment configuration as per user requests
    
    """
    deployment_type_map = {
        "frontend": Frontend_Deployment_Config,
        "backend": Backend_Deployment_Config,
        "fullstack": Fullstack_Deployment_Config,
    }

    deployment_class = deployment_type_map.get(deployment_type)
    if deployment_class:
        if deployment_type == "frontend":
            for lang_config in lang_configs:
                if lang_config["type"] == "frontend":
                    parsed_lang_config={key: value for key, value in lang_config.items() if value is not None}
                    nginx_configuration=create_nginx_config(deployment_type, **parsed_lang_config)
                    language_configuration=get_language_config(**parsed_lang_config)
                    return deployment_class(frontend_config=language_configuration, nginx_configuration=nginx_configuration)
        elif deployment_type == "backend":
            for lang_config in lang_configs:
                if lang_config["type"] == "backend":
                    parsed_lang_config={key: value for key, value in lang_config.items() if value is not None}
                    language_configuration=get_language_config(**parsed_lang_config)
                    return deployment_class(backend_config=language_configuration)
        elif deployment_type == "fullstack":
            frontend_config = None
            backend_config = None            
            for lang_config in lang_configs:
                if lang_config["type"] == "frontend":
                    parsed_lang_config={key: value for key, value in lang_config.items() if value is not None}
                    frontend_config = get_language_config(**parsed_lang_config)
                elif lang_config["type"] == "backend":
                    parsed_lang_config={key: value for key, value in lang_config.items() if value is not None}
                    backend_config = get_language_config(**parsed_lang_config)
            combined_lang_config={"frontend":vars(frontend_config), "backend":vars(backend_config)}
            nginx_configuration=create_nginx_config(deployment_type, **combined_lang_config)
            return deployment_class(frontend_config=frontend_config,backend_config=backend_config,nginx_configuration=nginx_configuration)
        else:
            raise ValueError("Deployment type is Invalid.")
    else:
        raise ValueError(f"Unsupported deployment type: {deployment_type}")


# data = {
#   "User_Id": "dk007",
#   "Project_Name": "myproject",
#   "Deployment_type": "fullstack",
#   "Language_Configs": [
#     {
#       "type": "backend",
#       "File_Name": "app.zip",
#       "LANGUAGE_TYPE": "python_flask",
#       "PORT": 5000,
#       "OUTPUT_DIR": None,
#       "INSTALL_COMMAND": None,
#       "BUILD_COMMAND": None,
#       "RUN_COMMAND": [
#         "python",
#         "app.py"
#       ],
#       "BACKEND_PATH":"/api"
#     },
#     {
#       "type": "frontend",
#       "File_Name": "app.zip",
#       "LANGUAGE_TYPE": "react",
#       "PORT": 3000,
#       "OUTPUT_DIR": "dist",
#       "INSTALL_COMMAND": "npm install",
#       "BUILD_COMMAND": "npm run build",
#       "RUN_COMMAND": [
#         "node",
#         "server.js"
#       ],
#       "FRONTEND_PATH":"/"
#     }
#   ]
# }

# deployment_config = create_deployment_config(data["Deployment_type"], data["Language_Configs"])
# # print(vars(deployment_config.frontend_config))
# print(vars(deployment_config))
# # print(deployment_config.nginx_configuration)