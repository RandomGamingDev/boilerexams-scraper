import os
import json
import glob
import shutil
import requests

from pathlib import Path

def clear_dir(path: str):
  for f in glob.glob(f"{str(path)}/*"):
    if os.path.isfile(f) or os.path.islink(f):
      os.remove(f)
    elif os.path.isdir(f):
      shutil.rmtree(f)

def main():
  JSON_INDENT = os.getenv("JSON_INDENT", 2)
  if JSON_INDENT is not None and not isinstance(JSON_INDENT, int):
    JSON_INDENT = None if JSON_INDENT.lower() == "none" else int(JSON_INDENT)

  QUESTIONS_OUT = Path(os.getenv("WORD_PATTERN_OUT", "./boilerexam-questions"))
  
  if os.path.isdir(QUESTIONS_OUT):
    clear_dir(QUESTIONS_OUT)
  else:
    os.makedirs(QUESTIONS_OUT)

  RESOURCES_OUT = QUESTIONS_OUT / "resources"
  os.mkdir(RESOURCES_OUT)

  RESOURCE_IMAGE_OUT = RESOURCES_OUT / "IMAGE"
  os.mkdir(RESOURCE_IMAGE_OUT)

  # Get Subjects' and courses
  try:
    res = requests.get("https://api.boilerexams.com/courses/subjects")
    res.raise_for_status()

    subjects = res.json()
    for subject in subjects:
      SUBJECT_OUT = QUESTIONS_OUT / subject["subject"]
      os.mkdir(SUBJECT_OUT)

      with open(SUBJECT_OUT / "subject.json", 'w') as f:
        json.dump(subject, f, indent=JSON_INDENT)

      for course in subject["courses"]:
        COURSE_OUT = SUBJECT_OUT / f"{course["abbreviation"]}{course["number"]}"
        os.mkdir(COURSE_OUT)

        with open(COURSE_OUT / "course.json", 'w') as f:
          json.dump(course, f, indent=JSON_INDENT)

        # Get Course's EXAM & TOPIC resources and their respective questions
        for study_mode in course["studyModes"]:
          study_resource_type = None
          match study_mode:
            case "EXAM":
              study_resource_type = "exams"
            case "TOPIC":
              study_resource_type = "topics"
            case _:
              continue

          STUDY_RESOURCES_OUT = COURSE_OUT / study_resource_type
          os.mkdir(STUDY_RESOURCES_OUT)

          res = requests.get(f"https://api.boilerexams.com/courses/{course["id"]}/{study_resource_type}")
          res.raise_for_status()

          study_resources = res.json()

          with open(STUDY_RESOURCES_OUT / f"{study_resource_type}.json", 'w') as f:
            json.dump(study_resources, f, indent=JSON_INDENT)

          for study_resource in study_resources:
            STUDY_RESOURCE_OUT = None
            match study_mode:
              case "EXAM":
                STUDY_RESOURCE_OUT = STUDY_RESOURCES_OUT / f"#{study_resource["number"]}-{study_resource["season"]},{study_resource["year"]}"
              case "TOPIC":
                STUDY_RESOURCE_OUT = STUDY_RESOURCES_OUT / f"{study_resource["name"]}"
              case _:
                continue
            os.mkdir(STUDY_RESOURCE_OUT)

            for question in study_resource["questions"]:
              res = requests.get(f"https://api.boilerexams.com/questions/{question["id"]}")
              res.raise_for_status()
              question_data = res.json()

              resources = question_data["resources"]
              if question_data["type"] == "MULTIPLE_CHOICE":
                resources.extend([resource for choice in question_data["data"]["answerChoices"] for resource in choice["resources"]])

              for resource in resources:
                if resource["type"] == "IMAGE":
                  img_res = requests.get(resource["data"]["url"], stream=True)
                  img_res.raise_for_status()

                  with open(RESOURCE_IMAGE_OUT / f"{resource["data"]["key"]}.png", "wb") as f:
                    for chunk in img_res.iter_content(chunk_size=8192):
                      f.write(chunk)

              with open(STUDY_RESOURCE_OUT / f"question-{question["number"]}.json", 'w') as f:
                json.dump(question_data, f, indent=JSON_INDENT)
  except requests.exceptions.RequestException as e:
    print(e)

if __name__ == "__main__":
  main()
