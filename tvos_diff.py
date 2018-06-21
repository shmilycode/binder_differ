#!/usr/bin/python3.2

import difflib
import argparse
import os.path


class FileParser:
    filename = ''
    def __init__(self, filename):
        self.filename = filename

'''
    def IsEmptyLine(self, line, IsSpaceJunk, IsTabJunk):
        is_empty = False
        if line=='':
            is_empty = True

        tmp_line = line
        if(!is_empty and IsSpaceJunk):
            tmp_line = line.strip()

        for character in tmp_line:
            if(character == ' ' && IsSpaceJunk):
                continue
            if(character == '\t' && IsTabJunk):
                continue
            is_empty = False
            break

        return is_empyt

    def RemoveEmptyLine(self, IsSpaceJunk, IsTabJunk):
        context = ''
        with open (self.filename, 'r') as reading_file:
            context = reading_file.read()
            context = context.splitlines()
            line_num = 0
            for line in context:
                if self.IsEmptyLine(line, IsSpaceJunk, IsTabJunk):
                    del context[line_num]
                line_num = line_num + 1

        return context
'''

class DiffParser:

    def IsDiff(line, IsPlus):
        ch = '+'
        if IsPlus is False:
            ch = '-'
        if line[0] == ch: 
            return True;
        else:
            return False;

    '''
    Compare to file, and return context with Diff infomation
    '''
    def CompareFile(file1_context, file2_context):
        result = list(difflib.ndiff(file1_context, file2_context))
        return result

    '''
    Return Diff list from @context
    '''
    def GetDiffContext(context):
        diff_list = []
        for line in context:
            if DiffParser.IsDiff(line, True) or DiffParser.IsDiff(line, False):
               diff_list.append(line)

        
        return diff_list

    '''
    Remove all the spaces and tabs at in the string
    '''
    def ClearSpaceAndTable(line):
        return line.replace(' ', '').replace('\t', '')    

    '''
    Remove '+' or '-' flag before the context
    '''

    '''
    If two line are opposit operation, for example, 
    + abc
    - abc
    is the opposit operation
    '''
    def IsOppositOpt(line1, line2):
        return ((line1[0] == '+' and line2[0] == '-') or (line1[0] == '-' and line2[0] == '+')) and (line1[1] == line2[1])

    def ParseDiffContext(context):
        parsed_diff_list = []
        tmp_parsed_list = []
        for line in context:
            if DiffParser.IsDiff(line, True) or DiffParser.IsDiff(line, False):
                new_line = ' ' + line[1:]
                tmp_line = DiffParser.ClearSpaceAndTable(new_line)

                if len(tmp_parsed_list) and DiffParser.IsOppositOpt((line[0], tmp_line),tmp_parsed_list[-1]):
                    del tmp_parsed_list[-1]
                    del parsed_diff_list[-1]
                else:
                    tmp_parsed_list.append((line[0], tmp_line))
                    parsed_diff_list.append(new_line)


                #if one is '-' and the other is '+', then remove it.

        return parsed_diff_list

class LibBaseParser:
    row_path = ''
    new_path = ''
    library_name = ''
    folder_name = ''
    diff_parser = DiffParser
    def __init__(self, row_path, new_path):
        self.row_path = row_path
        self.new_path = new_path
        folder_split = row_path.split('/')
        self.folder_name = folder_split[-1];
        idx = self.folder_name.find('manager')
        if idx != -1:
            self.library_name = self.folder_name[0:idx]

    def GetFolderName(self):
        return self.folder_name;

    def GetLibraryName(self):
        return self.library_name;

    def GetRowPath(self):
        return self.row_path;

    def GetNewPath(self):
        return self.new_path;

    def GetDiffParser(self):
        return self.diff_parser;

class LibManagerParser(LibBaseParser):

    def __init__(self, row_path, new_path):
        super().__init__(row_path, new_path)

    def CreateDiffContext(self):
        libmanager_name = 'lib'+super().GetFolderName();
        row_libmanager_path = super().GetRowPath() + '/' + libmanager_name
        new_libmanager_path = super().GetNewPath() + '/' + libmanager_name
        
        result = []
        if os.path.isdir(row_libmanager_path) and os.path.isdir(new_libmanager_path):
            libmanager_file_name = super().GetLibraryName().title() + 'Manager.cpp'
            row_libmanager_file = row_libmanager_path + '/' + libmanager_file_name;
            new_libmanager_file = new_libmanager_path + '/' + libmanager_file_name;
            if os.path.isfile(row_libmanager_file) and os.path.isfile(new_libmanager_file):
                with open (row_libmanager_file,'r') as f1:
                    with open (new_libmanager_file,'r') as f2:
                        f1_context = f1.read().splitlines()
                        f2_context = f2.read().splitlines()
                        diff_context = super().GetDiffParser().CompareFile(f1_context, f2_context)
                        #just get the whold diff and save it
                        diff_context = super().GetDiffParser().GetDiffContext(diff_context)
                        result = super().GetDiffParser().ParseDiffContext(diff_context)
            else:
                print("%s or %s is not a file!" % (file1, file2));

        return result
        
class ILibManagerParser(LibBaseParser):

    def __init__(self, row_path, new_path):
        super().__init__(row_path, new_path)

    def GetEnumRange(self, context):
        enum_line_number = -1
        enum_start = -1;
        enum_end = -1;
        for line in context:
            enum_line_number = enum_line_number + 1
            #find the start of enum defined
            if enum_start == -1:
                enum_pos = line.find('enum')
                if enum_pos == -1:
                    continue
                else:
                    enum_start = enum_line_number

            #find the end of enum defined
            bracket_pos = line.find('}')
            if bracket_pos == -1:
                continue
            else:
                enum_end = enum_line_number
                break;
        return enum_start,enum_end

    def CreateEnumDiffContext(self, enum_list):
        result = []
        result = super().GetDiffParser().GetDiffContext(enum_list)
        result = super().GetDiffParser().ParseDiffContext(result)

        return result

    def CreateFunctionDiffContext(self, function_list):
        return

    def CreateDiffContext(self):
        libmanager_name = 'lib'+super().GetFolderName();
        row_libmanager_path = super().GetRowPath() + '/' + libmanager_name
        new_libmanager_path = super().GetNewPath() + '/' + libmanager_name
         
        enum_result = []
        function_result = []
        if os.path.isdir(row_libmanager_path) and os.path.isdir(new_libmanager_path):
            libmanager_file_name = 'I' + super().GetLibraryName().title() + 'Manager.cpp'
            row_libmanager_file = row_libmanager_path + '/' + libmanager_file_name;
            new_libmanager_file = new_libmanager_path + '/' + libmanager_file_name;
            if os.path.isfile(row_libmanager_file) and os.path.isfile(new_libmanager_file):
                with open (row_libmanager_file,'r') as row_file:
                    with open (new_libmanager_file,'r') as new_file:
                        row_context = row_file.read().splitlines()
                        new_context = new_file.read().splitlines()
                        diff_context = super().GetDiffParser().CompareFile(row_context, new_context)

                        enum_start,enum_end = self.GetEnumRange(diff_context)
                        if enum_start != -1 and enum_end != -1:
                            enum_list = diff_context[enum_start : enum_end]
                        #first, find out the definition of enum list, and save it
                        enum_result = self.CreateEnumDiffContext(enum_list)
                        #second, get the function definition.
                        function_result = self.CreateFunctionDiffContext(diff_context[enum_end:])

            else:
                print("%s or %s is not a file!" % (file1, file2));

        return enum_result

def LibManagerTest(row_path, new_path):
    libmanager_parser = LibManagerParser(argv.row_file, argv.new_file)
    print('\n'.join(libmanager_parser.CreateDiffContext()))

def ILibManagerTest(row_path, new_path):
    Ilibmanager_parser = ILibManagerParser(row_path, new_path)
    print('\n'.join(Ilibmanager_parser.CreateDiffContext()))

if __name__ == '__main__':
    parse = argparse.ArgumentParser(description='manual to this script')
    parse.add_argument('--row_file', type=str, default=None)
    parse.add_argument('--new_file', type=str, default=None)
    argv = parse.parse_args()

    LibManagerTest(argv.row_file, argv.new_file)
