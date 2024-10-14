from sonarqube import SonarQubeClient
import gitlab
import logging
import config
logging.basicConfig(filename=config.log_filename,
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
try:
    sonar = SonarQubeClient(sonarqube_url=config.url_sonar, token=config.sonar_token)
    projects = sonar.projects.search_projects()

    gl = gitlab.Gitlab(config.gitlab_url, private_token=config.gitlab_token)


    projects_data = {}
    groups = gl.groups.list(get_all=True)
    for group in groups:
        for parser in config.list_git_groups:
            if group.full_path.startswith(parser):
                projects_from_git = gl.groups.get(group.id).projects.list(get_all=True)
                for project in projects_from_git:
                    pr = gl.projects.get(project.id)
                    projects_data[pr.name_with_namespace] = {'path_with_namespace': pr.path_with_namespace.replace('/', '-'), 'http_url_to_repo' : pr.http_url_to_repo}
    for k,v in projects_data.items():
        print("\'" + v['path_with_namespace'] + "\' : \'" + v['http_url_to_repo'] + "\' ,")
        try:
          # sonar.projects.delete_project(project=v['path_with_namespace'])
            sonar.projects.create_project(project=v['path_with_namespace'], name=k, visibility="public")
          # sonar.permissions.apply_template_to_project(templateName="ot_135", projects=v['path_with_namespace'])
        except Exception as error:
            print(error)

except Exception as errors:
    logging.error(f"Error: {errors}")
