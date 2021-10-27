from sarif_om import *
import os
import re
import tarfile

from src.output_parser.Parser import Parser
from src.output_parser.SarifHolder import isNotDuplicateRule, parseArtifact, parseRule, parseResult


class Manticore(Parser):

    @staticmethod
    def parseFile(content):
        output = []
        lines = content.splitlines()

        current_vul = None
        for line in lines:
            if len(line) == 0:
                continue
            if line[0] == '-':
                if current_vul is not None:
                    output.append(current_vul)
                current_vul = {
                    'name': line[1:-2].strip(),
                    'line': -1,
                    'code': None
                }
            elif current_vul is not None and line[:4] == '    ':
                index = line[4:].rindex('  ') + 4
                current_vul['line'] = int(line[4:index])
                current_vul['code'] = line[index:].strip()

        if current_vul is not None:
            output.append(current_vul)
        return output

    def parse(self):
        if os.path.exists(os.path.join(self.task.result_output_path(), 'result.tar')):
            out = []
            tar = tarfile.open(os.path.join(self.task.result_output_path(), 'result.tar'))
            m = re.findall('Results in /(mcore_.+)', self.str_output)
            for fout in m:
                output_file = tar.extractfile('results/' + fout + '/global.findings')
                out.append(Manticore.parseFile(output_file.read().decode('utf8')))
    
    def is_success(self) -> bool:
        return os.path.exists(os.path.join(self.task.result_output_path(), 'result.tar'))

    def parseSarif(self, manticore_output_results, file_path_in_repo):
        rulesList = []
        resultsList = []

        artifact = parseArtifact(uri=file_path_in_repo)

        for multipleAnalysis in manticore_output_results["analysis"]:
            for analysis in multipleAnalysis:
                rule = parseRule(tool="manticore", vulnerability=analysis["name"])
                result = parseResult(tool="manticore", vulnerability=analysis["name"], level="warning",
                                     uri=file_path_in_repo,
                                     line=analysis["line"], snippet=analysis["code"])

                resultsList.append(result)

                if isNotDuplicateRule(rule, rulesList):
                    rulesList.append(rule)

        tool = Tool(driver=ToolComponent(name="Manticore", version="0.3.5", rules=rulesList,
                                         information_uri="https://github.com/trailofbits/manticore",
                                         full_description=MultiformatMessageString(
                                             text="Manticore is a symbolic execution tool for analysis of smart contracts and binaries.")))

        run = Run(tool=tool, artifacts=[artifact], results=resultsList)

        return run
