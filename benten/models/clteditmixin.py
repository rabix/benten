"""Scaffolding features for CommandLineTool"""


class CltEditMixin:

    def add_docker(self, docker_image):
        edit, lines, indent = self.prefix_for_add_subsection(
            section_key="requirements",
            sub_section_key="DockerRequirement",
            key_field="class",
            prefer_dict=False)

        lines += [indent + "dockerPull: {}\n".format(docker_image)]

        edit.text = "\n".join(lines)
        return edit
