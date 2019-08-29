import logging
import re
import os

class FileProcessor:
    '''
    Base class for file processors.
    '''

    def process(self, dir_name, file_name):
        '''
        This method will be executed on the file specified by the arguments.
        This method needs to be implemented.
        :param dir_name: The path to the directory containing the file.
        :param file_name: The name of the file to be processed.
        :return:
        '''
        print ('Implement me!! Processing file_path: ' + dir_name + ' -> ' + file_name)
        return None


class DocTreeVisitor:
    '''
    This class executes a given function on the files conatined in a directory (including all its subdirectories).
    This class implements the the Visitor design pattern.
    '''
    def __init__(self, dirpath, inc=None, exc=None):
        '''
        :param dirpath: Path of the directory to explore.
        :param inc: List of regular expressions matching the files to be included into
         the processing. If left None, all files will be included.
        :param exc: List of regular expressions matching the files to be excluded into
         the processing among those cosidered as included in the inc parameter. If left
         None, no file will be excluded.
        '''
        self.dirpath = dirpath
        self.inc = inc
        self.exc = exc

        self.inc_reg_exps = []
        if inc:
            for e in inc:
                self.inc_reg_exps.append(re.compile(e))
        self.exc_reg_exps = []
        if exc:
            for e in exc:
                self.exc_reg_exps.append(re.compile(e))


    def process(self, file_processor):
        os.path.walk(self.dirpath, self._process_dir, file_processor)

    def _process_dir(self, file_processor, dirname, names):
        for name in names:
            path = os.path.join(dirname, name)
            if os.path.isfile(path):
                if self._matches(path):
                    file_processor.process(dirname, name)
                else:
                    logging.log(logging.INFO, 'File excluded: ' + path)

    def _matches(self, s):
        if len(self.inc_reg_exps) > 0:
            # Check wether file should not be included
            not_included = True
            for r in self.inc_reg_exps:
                if (r.match(s) != None):
                    not_included = False
                    break
            if not_included:
                return False

        if len(self.exc_reg_exps) > 0:
            # Check wether file should be excluded
            for r in self.exc_reg_exps:
                if (r.match(s) != None):
                    return False
        return True




