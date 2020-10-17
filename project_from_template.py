import json
import requests
import sys
from credentials import token


def select_template():
    templates = dict()
    i = 1
    projects = todoist.get("https://api.todoist.com/rest/v1/projects").json()
    for project in projects:
        if "[TEMPLATE]" in project["name"]:
            templates[str(i)] = {"name": project["name"], "id": project["id"]}
            i = i + 1

    print("Lista szablonów")
    for k in templates:
        print("%s: %s" % (k, templates[k]["name"]))

    selection = input("Wybierz szablon:")
    return templates[selection]


def get_template_sections(template):
    print("Reading template sections... ", end="")
    response = todoist.get("https://api.todoist.com/rest/v1/sections?project_id=%s" % template["id"])
    if response.status_code == 200:
        print("OK")
        return response.json()
    else:
        sys.exit("Failed")


def get_template_tasks(template):
    print("Reading template tasks... ", end="")
    response = todoist.get("https://api.todoist.com/rest/v1/tasks")
    if response.status_code == 200:
        print("OK")
        tasks = response.json()
        return [task for task in tasks if task["project_id"] == template["id"]]
    else:
        sys.exit("Failed")


def create_project(template):
    name = template["name"].replace("[TEMPLATE]", "").strip()
    print("Creating new project: %s... " % name, end="")
    response = todoist.post(
        "https://api.todoist.com/rest/v1/projects",
        data=json.dumps({
            "name": name
        }),
        headers={"Content-Type": "application/json"})
    if response.status_code == 200:
        print("CREATED")
        new_project = response.json()
        return new_project["id"]
    else:
        sys.exit("Failed")



def create_sections(sections, dest_id):
    section_dict = {0: 0}
    for section in sections:
        print("Creating section: %s... " % section["name"], end="")
        response = todoist.post(
            "https://api.todoist.com/rest/v1/sections",
            data=json.dumps({
                "project_id": dest_id,
                "name": section["name"]
            }),
            headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            print("CREATED")
        else:
            sys.exit("Failed")
        s = response.json()
        section_dict[section["id"]] = s["id"]
    return section_dict


def create_tasks(tasks, dest_sections, dest_id):
    for task in tasks:
        print("Creating task: %s... " % task["content"], end="")
        response = todoist.post(
            "https://api.todoist.com/rest/v1/tasks",
            data=json.dumps({
                "content": task["content"],
                "project_id": dest_id,
                "section_id": dest_sections[task["section_id"]]
            }),
            headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            print("CREATED")
        else:
            sys.exit("Failed")


todoist = requests.Session()
todoist.headers.update({"Authorization": "Bearer %s" % token})

template = select_template()
template_sections = get_template_sections(template)
template_tasks = get_template_tasks(template)

new_project_id = create_project(template)
new_project_sections = create_sections(template_sections, new_project_id)
create_tasks(template_tasks, new_project_sections, new_project_id)


