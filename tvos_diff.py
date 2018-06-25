#!/usr/bin/python3.2

import difflib
import argparse
import os.path
import re


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
    If two line are opposit operation, for example, 
    + abc
    - abc
    is the opposit operation
    '''
    def IsOppositOpt(line1, line2):
        return ((line1[0] == '+' and line2[0] == '-') or (line1[0] == '-' and line2[0] == '+')) and (line1[1] == line2[1])

    '''
    Remove '+' or '-' flag before the context
    '''
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



    def IsEmptyLine(line, IsSpaceJunk, IsTabJunk):
        is_empty = False
        tmp_str = line
        if IsSpaceJunk == True:
            tmp_str = tmp_str.replace(' ', '')

        if IsTabJunk == True:
            tmp_str = tmp_str.replace('\t', '')
        return tmp_str == ''

class FunctionParser:
    '''
    Get function name, include the list of parameter, 
    like function @void start(int a, int b), return @start(int a, int b)
    '''
    def GetFunctionName(declaration):
        #Get function name
        matchObj = re.search(r'virtual( +)(\w+?)( +)(.*?);', declaration)
        function_name = ''
        if matchObj:
            function_name = matchObj.group(4)
        else:
            matchObj = re.search(r'(\w+?)( +)(.*?);', declaration)
            if matchObj:
                function_name = matchObj.group(3)

        return function_name

    '''
    Get function name, haven't include the list of parameter, 
    like function @void start(int a, int b), only return @start
    '''
    def GetRowFunctionName(declaration):
        #Get function name
        matchObj = re.search(r'virtual( +)(\w+?)( +)(.*?)\(.*?\);', declaration)
        function_name = ''
        if matchObj:
            function_name = matchObj.group(4)
        else:
            matchObj = re.search(r'(\w+?)( +)(.*?)\(.*?\);', declaration)
            if matchObj:
                function_name = matchObj.group(3)

        return function_name
    '''
    From @start_pos, gain the completed definition of function, the function must start with '{'
        and end with '}'
    '''
    def GetFunctionDefinition(start_pos, context):
        bracket_count = 0
        definition_list = []
        for line in context[start_pos+1:]:
            definition_list.append(line)
            #Judge from @1, because the @0 item maybe the '+' or '-'
            skip_pos = 0
            if line != '' and (line[0] == '+' or line[0] == '-'):
                skip_pos = 1
            if DiffParser.ClearSpaceAndTable(line[skip_pos:]) == '{':
                bracket_count =  bracket_count + 1;
            elif DiffParser.ClearSpaceAndTable(line[skip_pos:]) == '}':
                bracket_count = bracket_count - 1;
                if bracket_count == 0:
                    break;

        return definition_list;

    '''
    the @diff_context must get from header file, and only contain the function declaration
    '''
    def GetAppendFunction(context):
        parsed_diff_list = []
        tmp_parsed_list = []
        for line in context:
            if DiffParser.IsDiff(line, True) or DiffParser.IsDiff(line, False):
                new_line = ' ' + line[1:]
                function_name = FunctionParser.GetRowFunctionName(line)
                tmp_line = DiffParser.ClearSpaceAndTable(function_name)

                if len(tmp_parsed_list) and DiffParser.IsOppositOpt((line[0], tmp_line),tmp_parsed_list[-1]):
                    del tmp_parsed_list[-1]
                    del parsed_diff_list[-1]
                else:
                    tmp_parsed_list.append((line[0], tmp_line))
                    parsed_diff_list.append(new_line)

        return parsed_diff_list

    def GetAppendEnum(context):
        parsed_diff_list = []
        tmp_parsed_list = []
        for line in context:
            if DiffParser.IsDiff(line, True) or DiffParser.IsDiff(line, False):
                new_line = ' ' + line[1:]
                tmp_line = DiffParser.ClearSpaceAndTable(new_line)
                if tmp_line != '' and tmp_line[-1] == ',':
                    tmp_line = tmp_line[:-1]

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
        manager_idx = self.folder_name.endswith('manager')
        if self.folder_name.endswith('manager'):
            manager_idx = self.folder_name.find('manager')
            self.library_name = self.folder_name[0:manager_idx]
        elif self.folder_name.endswith('impl'):
            impl_idx = self.folder_name.find('impl')
            self.library_name = self.folder_name[0:impl_idx]

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

    def GetRealFileName(self, path, file_name):
        file_list = os.listdir(path)
        file_name = file_name.lower()
        for sub_file_name in file_list:
            tmp_sub_file_name = sub_file_name.lower()
            if file_name == tmp_sub_file_name:
                return sub_file_name
        return file_name

    def GetHeaderPath(self, libname_prefix, libname_suffix, filename_prefix, filename_suffix):
        libmanager_name = libname_prefix + self.GetFolderName() + libname_suffix;
        row_libmanager_path = self.GetRowPath() + '/../include/' + libmanager_name
        new_libmanager_path = self.GetNewPath() + '/../include/' + libmanager_name
        row_libmanager_file = ''
        new_libmanager_file = ''

        if os.path.isdir(row_libmanager_path) and os.path.isdir(new_libmanager_path):
            libmanager_file_name = filename_prefix + self.GetLibraryName().title() + 'Manager' + filename_suffix;
            libmanager_file_name = self.GetRealFileName(new_libmanager_path, libmanager_file_name)

            row_libmanager_file = row_libmanager_path + '/' + libmanager_file_name;
            new_libmanager_file = new_libmanager_path + '/' + libmanager_file_name;
            if os.path.isfile(row_libmanager_file) == False and os.path.isfile(new_libmanager_file) == False:
                libmanager_file_name = filename_prefix + self.GetLibraryName().title() + 'Impl' + filename_suffix;
                libmanager_file_name = self.GetRealFileName(new_libmanager_path, libmanager_file_name)

                row_libmanager_file = row_libmanager_path + '/' + libmanager_file_name;
                new_libmanager_file = new_libmanager_path + '/' + libmanager_file_name;
        else:
            print("%s or %s is not a DIR" % (row_libmanager_path, new_libmanager_path))

        return  row_libmanager_file,new_libmanager_file

    def GetSourcePath(self, libname_prefix, libname_suffix, filename_prefix, filename_suffix):
        row_libmanager_file = ''
        new_libmanager_file = ''
        libmanager_name = libname_prefix+self.GetFolderName() + libname_suffix;
        row_libmanager_path = self.GetRowPath() + '/' + libmanager_name
        new_libmanager_path = self.GetNewPath() + '/' + libmanager_name
        #print(row_libmanager_path)
        #print(new_libmanager_path)
        if os.path.isdir(row_libmanager_path) and os.path.isdir(new_libmanager_path):
            libmanager_file_name = filename_prefix + self.GetLibraryName().title() + 'Manager' + filename_suffix;
            libmanager_file_name = self.GetRealFileName(new_libmanager_path, libmanager_file_name)

            row_libmanager_file = row_libmanager_path + '/' + libmanager_file_name;
            new_libmanager_file = new_libmanager_path + '/' + libmanager_file_name;
            if os.path.isfile(row_libmanager_file) == False and os.path.isfile(new_libmanager_file) == False:
                libmanager_file_name = filename_prefix + self.GetLibraryName().title() + 'Impl' + filename_suffix
                libmanager_file_name = self.GetRealFileName(new_libmanager_path, libmanager_file_name)

                row_libmanager_file = row_libmanager_path + '/' + libmanager_file_name;
                new_libmanager_file = new_libmanager_path + '/' + libmanager_file_name;

        return  row_libmanager_file,new_libmanager_file

class LibManagerParser(LibBaseParser):

    def __init__(self, row_path, new_path):
        super().__init__(row_path, new_path)

    def CreateHeaderDiffContext(self):
        row_libmanager_file,new_libmanager_file = super().GetHeaderPath('', '', '', '.h')
        result = []
        if os.path.isfile(row_libmanager_file) and os.path.isfile(new_libmanager_file):
            with open (row_libmanager_file,'r',encoding='ISO-8859-15') as f1:
                with open (new_libmanager_file,'r',encoding='ISO-8859-15') as f2:
                    f1_context = f1.read().splitlines()
                    f2_context = f2.read().splitlines()
                    diff_context = super().GetDiffParser().CompareFile(f1_context, f2_context)
                    diff_context = super().GetDiffParser().GetDiffContext(diff_context)
                    result = FunctionParser.GetAppendFunction(diff_context)
        else:
            print("%s or %s is not a file!" % (row_libmanager_file, new_libmanager_file));


        return result

    def CreateSourceDiffContext(self, declaration_list):
        row_libmanager_file,new_libmanager_file = super().GetSourcePath('lib', '', '', '.cpp')
        result = []
        if os.path.isfile(row_libmanager_file) and os.path.isfile(new_libmanager_file):
            with open (row_libmanager_file,'r') as f1:
                with open (new_libmanager_file,'r') as f2:
                    f1_context = f1.read().splitlines()
                    f2_context = f2.read().splitlines()
                    diff_context = super().GetDiffParser().CompareFile(f1_context, f2_context)
                    #just get the whold diff and save it
                    result = self.GetExtendHeader(diff_context)
                    result.extend(self.GetFunctionDefintion(f2_context, declaration_list, '::'))
        else:
            print("%s or %s is not a file!" % (row_libmanager_file, new_libmanager_file));
        return result

    def GetExtendHeader(self, diff_context):
        result = []
        diff_context = DiffParser.GetDiffContext(diff_context)
        diff_context = DiffParser.ParseDiffContext(diff_context)
        for line in diff_context:
            if line.find('#include') != -1:
                line = line.strip()
                result.append(line)

        return result

    def GetFunctionDefintion(self, context, declaration_list, function_name_prefix):
        definitions_list = []
        for declaration in declaration_list:
            #print(declaration)
            #Get function name
            function_name = FunctionParser.GetFunctionName(declaration)
            if function_name != '':
                function_name = DiffParser.ClearSpaceAndTable(function_name)
                for line in context:
                    tmp_line = DiffParser.ClearSpaceAndTable(line)
                    if tmp_line.find(function_name_prefix+function_name) != -1:
                        definition = [line, ]
                        definition.extend(FunctionParser.GetFunctionDefinition(context.index(line), context))
                        definitions_list.extend(definition)

        return definitions_list


class ILibManagerParser(LibBaseParser):

    def __init__(self, row_path, new_path):
        super().__init__(row_path, new_path)

    '''
    '''
    def GetRange(self, context, start_string, end_string):
        start_pos = -1;
        end_pos = -1;
        for line in context:
            #find the start of enum defined
            if start_pos == -1:
                start_str_pos = line.find(start_string)
                if start_str_pos == -1:
                    continue
                else:
                    start_pos = context.index(line)

            #find the end of enum defined
            end_str_pos = line.find(end_string)
            if end_str_pos == -1:
                continue
            else:
                end_pos = context.index(line)
                break;
        return start_pos,end_pos

    '''
    Get Diff Enum list from @enum_list
    '''
    def CreateEnumDiffContext(self, enum_list):
        result = []
        result = super().GetDiffParser().GetDiffContext(enum_list)
        result = FunctionParser.GetAppendEnum(result)

        return result



    '''
    According the declaration, get the definition of functions
    '''
    def GetDiffDefinition(self, declaration_list, context):
        definitions_list = []
        for declaration in declaration_list:
            #Get function name
            function_name = FunctionParser.GetFunctionName(declaration)
            if function_name != '':
                function_name = DiffParser.ClearSpaceAndTable(function_name)
                for line in context:
                    tmp_line = DiffParser.ClearSpaceAndTable(line)
                    if tmp_line.find(function_name) != -1:
                        definition = [declaration[4 : len(declaration)-1], ]
                        definition.extend(FunctionParser.GetFunctionDefinition(context.index(line), context))
                        definitions_list.extend(definition)

        #replace all the '+' and '-' in the defintion
        pattern = ['+','-']
        definitions_list = [' ' + x[1:] if x[0] in pattern else x for x in definitions_list]

        return definitions_list
        

    '''
    Get Diff function definition for Bp*Manager class
    '''
    def CreateFunctionDiffContext(self, function_list):
        result = []
        declaration_start,declaration_end = self.GetRange(function_list, 'class', '}')
        #print(str(declaration_start) + ":" + str(declaration_end))
        declaration_list = []
        if declaration_start != -1 and declaration_end != -1:
            declaration_list = function_list[declaration_start : declaration_end]
        declaration_list = super().GetDiffParser().GetDiffContext(declaration_list)
        declaration_list = FunctionParser.GetAppendFunction(declaration_list)
        #print('\n'.join(declaration_list))
        definition_start, definition_end = self.GetRange(function_list, 'class', '::onTransact')
        result = self.GetDiffDefinition(declaration_list, function_list[declaration_end:definition_end])
        return result

    '''
    Search the case implement in function transact
    '''
    def GetCaseImplement(self, transact_context, enum_def):
        case_start = -1
        case_end = -1
        result = []
        for line in transact_context:
           clear_line = DiffParser.ClearSpaceAndTable(line)
           if case_start == -1:
               if clear_line.find('case'+enum_def+':') != -1:
                   case_start = transact_context.index(line)
               else:
                   continue
           elif clear_line.find('case') != -1 or clear_line.find('default') != -1:
               case_end = transact_context.index(line)
               break

        if case_start != -1 and case_end != -1:
            result = transact_context[case_start : case_end]
    
        return result

    '''
    Use pointed @enum_def to get it's implements
    '''
    def GetDiffTransact(self, transact_context, enum_context):
        result = []
        for enum_def in enum_context:
            enum_def = DiffParser.ClearSpaceAndTable(enum_def)
            if enum_def != '' and enum_def[-1] == ',':
                enum_def = enum_def[0 : -1]
            result.extend(self.GetCaseImplement(transact_context, enum_def))

        return result

    '''
    According to the @enum_result, gain the complted case implements in @::onTransact function
    '''
    def CreateCaseDiffContext(self, context, enum_result):
        result = []
        transact_start, transact_end = self.GetRange(context, '::onTransact', 'default')
        if transact_start != -1 and transact_end != -1:
            result = self.GetDiffTransact(context[transact_start : transact_end], enum_result)

        #replace all the '+' and '-' in the defintion
        pattern = ['+','-']
        result = [' ' + x[1:] if x[0] in pattern else x for x in result]
        return result
                
    def ParseDiffContext(self, row_libmanager_file, new_libmanager_file):
        enum_result = []
        function_result = []
        case_result = []
        if os.path.isfile(row_libmanager_file) and os.path.isfile(new_libmanager_file):
            with open (row_libmanager_file,'r') as row_file:
                with open (new_libmanager_file,'r') as new_file:
                    row_context = row_file.read().splitlines()
                    new_context = new_file.read().splitlines()
                    diff_context = super().GetDiffParser().CompareFile(row_context, new_context)

                    enum_start,enum_end = self.GetRange(diff_context, 'enum', '}')
                    if enum_start != -1 and enum_end != -1:
                        enum_list = diff_context[enum_start : enum_end]
                    #first, find out the definition of enum list, and save it
                    enum_result = self.CreateEnumDiffContext(enum_list)
                    #second, get the function definition.
                    function_result = self.CreateFunctionDiffContext(diff_context[enum_end+1:])
                    #third, get the 'case' implement.
                    case_result = self.CreateCaseDiffContext(diff_context, enum_result)
        else:
                print("%s or %s is not a file!" % (row_libmanager_file, new_libmanager_file));
        
        return enum_result, function_result, case_result

    def CreateHeaderDiffContext(self):
        result = []
        row_libmanager_file,new_libmanager_file = super().GetHeaderPath('', '', 'I', '.h')

        if os.path.isfile(row_libmanager_file) and os.path.isfile(new_libmanager_file):
            with open (row_libmanager_file,'r') as f1:
                with open (new_libmanager_file,'r') as f2:
                    f1_context = f1.read().splitlines()
                    f2_context = f2.read().splitlines()
                    diff_context = super().GetDiffParser().CompareFile(f1_context, f2_context)
                    diff_context = super().GetDiffParser().GetDiffContext(diff_context)
                    result = FunctionParser.GetAppendFunction(diff_context)
        else:
            print("%s or %s is not a file!" % (row_libmanager_file, new_libmanager_file));

        return result

    def CreateSourceDiffContext(self):
        row_libmanager_file,new_libmanager_file = super().GetSourcePath('lib', '', 'I', '.cpp')

        enum_result, function_result, case_result = self.ParseDiffContext(row_libmanager_file, new_libmanager_file)
        return enum_result, function_result, case_result

class ILibManagerClientParser(ILibManagerParser):
    def __init__(self, row_path, new_path):
        super().__init__(row_path, new_path)

    def CreateSourceDiffContext(self):
        enum_result = []
        function_result = []
        case_result = []
        row_libmanager_file,new_libmanager_file = super().GetSourcePath('lib', '', 'I', 'Client.cpp')
        enum_result, function_result, case_result = super().ParseDiffContext(row_libmanager_file, new_libmanager_file)

        return enum_result, function_result, case_result

class LibManagerServiceParser(LibManagerParser):
    def __init__(self,row_path, new_path):
        super().__init__(row_path, new_path)

    def CreateHeaderDiffContext(self):
        result = []
        row_libmanager_file,new_libmanager_file = super().GetSourcePath('lib', 'service', '', 'Service.h')
        if os.path.isfile(row_libmanager_file) and os.path.isfile(new_libmanager_file):
            with open (row_libmanager_file,'r') as f1:
                with open (new_libmanager_file,'r') as f2:
                    f1_context = f1.read().splitlines()
                    f2_context = f2.read().splitlines()
                    diff_context = super().GetDiffParser().CompareFile(f1_context, f2_context)
                    #just get the whold diff and save it
                    diff_context = super().GetDiffParser().GetDiffContext(diff_context)
                    result = FunctionParser.GetAppendFunction(diff_context)
        else:
            print("%s or %s is not a file!" % (row_libmanager_file, new_libmanager_file));

        return result   


    def CreateSourceDiffContext(self, declaration_list):
        result = []
        row_libmanager_file,new_libmanager_file = super().GetSourcePath('lib', 'service', '', 'Service.cpp')

        if os.path.isfile(row_libmanager_file) and os.path.isfile(new_libmanager_file):
            with open (row_libmanager_file,'r') as f1:
                with open (new_libmanager_file,'r') as f2:
                    f1_context = f1.read().splitlines()
                    f2_context = f2.read().splitlines()
                    diff_context = DiffParser.CompareFile(f1_context, f2_context)
                    result = super().GetExtendHeader(diff_context)
                    result.extend(super().GetFunctionDefintion(f2_context, declaration_list, '::Client::'))
        else:
            print("%s or %s is not a file!" % (row_libmanager_file, new_libmanager_file));

        return result   

def LibManagerTest(row_path, new_path):
    libmanager_parser = LibManagerParser(argv.row_file, argv.new_file)
    header_list = libmanager_parser.CreateHeaderDiffContext()
    print('\n'.join(header_list))
    print('\n'.join(libmanager_parser.CreateSourceDiffContext(header_list)))

def ILibManagerTest(row_path, new_path):
    Ilibmanager_parser = ILibManagerParser(row_path, new_path)
    enum_result, function_result, case_result = Ilibmanager_parser.CreateSourceDiffContext()
    header_context = Ilibmanager_parser.CreateHeaderDiffContext()
    print('\n'.join(enum_result))
    print('\n'.join(function_result))
    print('\n'.join(case_result))
    print('\n'.join(header_context))

def ILibManagerClientTest(row_path, new_path):
    Ilibmanager_parser = ILibManagerClientParser(row_path, new_path)
    enum_result, function_result, case_result = Ilibmanager_parser.CreateSourceDiffContext()
    print('\n'.join(enum_result))
    print('\n'.join(function_result))
    print('\n'.join(case_result))


def ConstructExtendLibManagerHeader(row_path, new_path):
    if os.isdir(row_path) or os.isdir(new_path):
        return
    else:
        print("ConstructExtendLibManagerHeader: %s or %s is not directory!" % (row_path, new_path));

    libmanager_parser = LibManagerParser(row_path, new_path)
    header_list = libmanager_parser.CreateHeaderDiffContext()
    definition_list = libmanager_parser.CreateSourceDiffContext(header_list)


def LibManagerServcieTest(row_path, new_path):
    libmanager_parser = LibManagerServiceParser(row_path, new_path)
    header_function = libmanager_parser.CreateHeaderDiffContext()
    source_function = libmanager_parser.CreateSourceDiffContext(header_function)
    print('\n'.join(header_function))
    print('\n'.join(source_function))

class TvosParser:
    def ParseLibManager(row_path, new_path):
        #parse libmanager
        libmanager_parser = LibManagerParser(row_path, new_path)
        header_list = libmanager_parser.CreateHeaderDiffContext()
        definition_list = libmanager_parser.CreateSourceDiffContext(header_list)
        row_libmanager_file,new_libmanager_header_file = libmanager_parser.GetHeaderPath('', '', 'CVT', 'Declaration.h')
        if header_list:
            with open(new_libmanager_header_file, 'w') as new_libmanager_header:
                new_libmanager_header.write('\n'.join(header_list))

        row_libmanager_file,new_libmanager_definition_file = libmanager_parser.GetHeaderPath('', '', 'CVT', 'Definition.h')
        if definition_list:
            with open(new_libmanager_definition_file, 'w') as new_libmanager_definition:
                new_libmanager_definition.write('\n'.join(definition_list))

    def ParseILibManager(row_path, new_path):
        #parse libmanager
        Ilibmanager_parser = ILibManagerParser(row_path, new_path)
        enum_result, function_result, case_result = Ilibmanager_parser.CreateSourceDiffContext()
        header_context = Ilibmanager_parser.CreateHeaderDiffContext()

        row_libmanager_file,new_enum_file = Ilibmanager_parser.GetHeaderPath('', '', 'CVTI', 'Enum.h')
        if enum_result:
            with open(new_enum_file, 'w') as new_enum_header:
                new_enum_header.write('\n'.join(enum_result))

        row_libmanager_file,new_function_definition_file = Ilibmanager_parser.GetHeaderPath('', '', 'CVTI', 'Function.h')
        if function_result:
            with open(new_function_definition_file, 'w') as function_definition_file:
                function_definition_file.write('\n'.join(function_result))

        row_libmanager_file,new_case_file = Ilibmanager_parser.GetHeaderPath('', '', 'CVTI', 'Case.h')
        if case_result:
            with open(new_case_file, 'w') as case_file:
                case_file.write('\n'.join(case_result))

        row_libmanager_file,new_libmanager_include_file = Ilibmanager_parser.GetHeaderPath('', '', 'CVTI', '.h')
        if header_context:
            with open(new_libmanager_include_file, 'w') as libmanager_include_file:
                libmanager_include_file.write('\n'.join(header_context))

    def ParseILibManagerClient(row_path, new_path):
        #parse libmanager
        libmanager_client_parser = ILibManagerClientParser(row_path, new_path)
        enum_result, function_result, case_result = libmanager_client_parser.CreateSourceDiffContext()

        row_libmanager_file,new_enum_file = libmanager_client_parser.GetHeaderPath('', '', 'CVTI', 'ClientEnum.h')
        if enum_result:
            with open(new_enum_file, 'w') as new_enum_header:
                new_enum_header.write('\n'.join(enum_result))

        row_libmanager_file,new_function_definition_file = libmanager_client_parser.GetHeaderPath('', '', 'CVTI', 'ClientFunction.h')
        if function_result:
            with open(new_function_definition_file, 'w') as function_definition_file:
                function_definition_file.write('\n'.join(function_result))

        row_libmanager_file,new_case_file = libmanager_client_parser.GetHeaderPath('', '', 'CVTI', 'ClientCase.h')
        if case_result:
            with open(new_case_file, 'w') as case_file:
                case_file.write('\n'.join(case_result))

    def ParseLibManagerService(row_path, new_path):
        libmanager_parser = LibManagerServiceParser(row_path, new_path)
        header_list = libmanager_parser.CreateHeaderDiffContext()
        definition_list = libmanager_parser.CreateSourceDiffContext(header_list)

        row_libmanager_file,new_libmanager_header_file = libmanager_parser.GetSourcePath('lib', '', 'CVT', 'ServiceDeclaration.h')
        if header_list:
            with open(new_libmanager_header_file, 'w') as new_libmanager_header:
                new_libmanager_header.write('\n'.join(header_list))

        row_libmanager_file,new_libmanager_definition_file = libmanager_parser.GetSourcePath('lib', '', 'CVT', 'ServiceDefinition.h')
        if definition_list:
            with open(new_libmanager_definition_file, 'w') as new_libmanager_definition:
                new_libmanager_definition.write('\n'.join(definition_list))

def ParseTvosLibrary(row_path, new_path):
    TvosParser.ParseLibManager(row_path, new_path)
    TvosParser.ParseILibManager(row_path, new_path)
    TvosParser.ParseILibManagerClient(row_path, new_path)
    TvosParser.ParseLibManagerService(row_path, new_path)

def TravelAllFolders(row_tvos_file, new_tvos_file):
    folders = os.listdir(row_tvos_file)
    for sub_folder in folders:
        if(sub_folder == 'include'):
            continue
        row_folder_path = row_tvos_file + '/' + sub_folder
        new_folder_path = new_tvos_file + '/' + sub_folder
        print("Parsing %s" % sub_folder)
        if os.path.isdir(row_folder_path) and os.path.isdir(new_folder_path):
            ParseTvosLibrary(row_folder_path, new_folder_path)
        else:
            print("%s or %s is not a path!!!" % (row_folder_path, new_folder_path))


if __name__ == '__main__':
    parse = argparse.ArgumentParser(description='manual to this script')
    parse.add_argument('--row_file', type=str, default=None)
    parse.add_argument('--new_file', type=str, default=None)
    parse.add_argument('--test', type=str, default=None)
    argv = parse.parse_args()

    if argv.test == '1':
        LibManagerTest(argv.row_file, argv.new_file)
    elif argv.test == '2':
        ILibManagerTest(argv.row_file, argv.new_file)
    elif argv.test == '3':
        ILibManagerClientTest(argv.row_file, argv.new_file)
    elif argv.test == '4':
        LibManagerServcieTest(argv.row_file, argv.new_file)
    elif argv.test == '0':
        TravelAllFolders(argv.row_file, argv.new_file)
