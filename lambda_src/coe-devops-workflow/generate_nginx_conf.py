def generate_nginx_config(**kwargs):
    """
    Generates a Nginx configuration file based on the provided arguments.

    Args:
        frontend_path (str): The path to the frontend application. Default is '/'.
        backend_path (str): The path to the backend application. Default is '/api'.
        frontend_ip (str): The IP address of the frontend application. Default is 'localhost'.
        backend_ip (str): The IP address of the backend application. Default is 'localhost'.
        frontend_port (str): The port number of the frontend application. Default is '3000'.

    Returns:
        str: The generated Nginx configuration file.
    """
    language_type = kwargs.get('language_type')
    deployment_type = kwargs.get('deployment_type')
    frontend_path = kwargs.get('frontend_path', '/')
    backend_path = kwargs.get('backend_path', '/api')
    frontend_ip = kwargs.get('frontend_ip', 'localhost')
    backend_ip = kwargs.get('backend_ip', 'localhost')
    frontend_port = kwargs.get('frontend_port', '3000')
    backend_port = kwargs.get('backend_port', '5000')
    
    config = None    
    if language_type == "nextjs":

        config=f"""
            server {{
                listen 80;
                location {frontend_path} {{
                    proxy_pass http://{frontend_ip}:{frontend_port};
                    proxy_set_header Host $host;
                    proxy_set_header X-Real-IP $remote_addr;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                    proxy_set_header X-Forwarded-Proto $scheme;
            }}
        
        """

        if deployment_type == "fullstack":
            config+=f"""
            location {backend_path} {{
                proxy_pass http://{backend_ip}:{backend_port};
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
            }}
            """
        config+="}"
        
    if language_type == "react":
        config =f"""
            server {{
                listen 80;

                location / {{
                root   /usr/share/nginx/html;
                index  index.html index.htm;
                try_files $uri /index.html =404;
                    }}
                
                """
        if deployment_type == "fullstack":
            config += f"""
            location {backend_path} {{
                proxy_pass http://{backend_ip}:{backend_port};
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
            }}
            """
        config+="}"
    return config