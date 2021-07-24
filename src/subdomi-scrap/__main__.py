from os import name
import os.path
from bs4 import BeautifulSoup
import requests
import re
from time import sleep
import argparse
from pathlib import Path
import threading
'''

Aim : Finds subdomains of valid domain address.

Medhod : via scrap from crt.sh thus your ip address or your id is being non-visible.

'''
stop_threads = False

class NetworkHand:
    BASE_URL = 'https://crt.sh/?q='

    def __init__(self, domain) -> None:
        self.domain = self.edit_domain(domain)
        self.full_url = self.create_url(self.domain)

    def create_url(self, domain) -> str:
        '''
        params: url\n
        returns: Returns a url: BASE_URL + given_domain:
        '''
        return ''.join([self.BASE_URL, domain])

    def edit_domain(self, domain) -> str:
        domain.strip()
        domain.lower()
        if check_domain(domain):
            domain = domain[find_first_dot_of(domain)() + 1:]
        return domain


    def get_responce(self):
        global stop_threads
        try:
            t1.start()
            responce = requests.get(self.full_url, timeout=(3.05, 27))
            if responce:
                stop_threads = True
                t1.join()
            else:
                print('\n\nNo respence from the recorce. Try Later.')
                exit()
        except (requests.ConnectionError, requests.Timeout) as exception:
            if exception:
                stop_threads = True
                t1.join()
                print('\n\nConnection error. Check your Net.')
                exit()
        return responce


class ParseHand:

    def __init__(self, domain) -> None:
        self.domain = domain
        self.network_1 = NetworkHand(self.domain)

    def soup_parse(self, html):
        soup_a = BeautifulSoup(html.text, 'html.parser')
        return soup_a

    def find_tds(self) -> list:
        '''
        :params: no param:
        :returns: : 
        '''
        tdList = []
        
        all_td = self.soup_parse(self.network_1.get_responce()).find_all('td')
        for td in all_td:
            if td.attrs.get('class') or td.attrs.get('style'):
                continue
            else:
                tdList.append(td.text)
        return tdList

    def saperate_texts(self, topleveldom) -> set:
        tdList = self.find_tds()
        td_list_column_6 = []
        new_td_list_column_6 = []

        for i in range(len(tdList)):
            if i == 1 or i % 3 == 1:
                td_list_column_6.append(tdList[i].strip())

        for link in td_list_column_6:
            link = str(link)
            x = re.findall(topleveldom, link)
            if len(x) > 1:
                a = re.split(topleveldom, link)
                for j in a:
                    if j == False:
                        continue
                    new_td_list_column_6.append(''.join([j, topleveldom]))
            else:
                new_td_list_column_6.append(link)

        k = list()
        for i in new_td_list_column_6:
            if i[0] == '.':
                k.append(i[3:] + i[:3])
            else:
                k.append(i)

        tdSet_column_6 = set(k)
        return tdSet_column_6


class FileHand:

    def __init__(self, location, filename, content) -> None:
        self.location = location
        self.filename = filename
        self.content = content

    def write_file(self):
        file_path = merge_paths([self.location, self.filename])
        with open(f'{file_path}', 'w', encoding='utf-8') as file:
            file.write('\n'.join(self.content))
        if os.path.exists(file_path):
            print('\n\n..Succesfully..')
            print(f'Check this adress: {self.location}')

  
def print_d(text='\nPlease Wait', delay=.5):
    print(end=text)
    n_dots = 0

    while True:
        if stop_threads:
            break
        elif n_dots == 3:
            print(end='\b\b\b', flush=True)
            print(end='   ', flush=True)
            print(end='\b\b\b', flush=True)
            n_dots = 0
        else:
            print(end='.', flush=True)
            n_dots += 1
        sleep(delay)

t1 = threading.Thread(target=print_d)

def get_check_os() -> str:
    '''
    :param : no param:
    :aim: tells us what is the os:
    '''
    if name == 'nt':
        return 'windows'
    elif name == 'posix':
        return 'linux'


def merge_paths(fuse_paths: list) -> str:
    '''
    :aim: this function takes a list and then merger them: 
    :return: returns a str  
    '''
    os_name = get_check_os()
    if os_name == 'windows':
        return '\\'.join(fuse_paths)
    elif os_name == 'linux':
        return '/'.join(fuse_paths)


def user_args_fun() -> tuple:
    '''
    :params: no param:
    :returns: returns a tuple that user entried:
    '''
    description = 'This application allows you to save the subdomains of the sites in a file.'
    domanin_help = 'type a domain address which you want to learn subdomain address'
    outfile_help = 'type a file name'
    path_help = 'type a path where you want to save'
    path_default = merge_paths([str(Path.home()), 'Desktop'])
    file_name_default = 'file_name'

    parser = argparse.ArgumentParser(description=description, prog='subdomi-scrap')
    parser.add_argument('-d', '--domain', help=domanin_help,
                        default='https:\\www.youtube.com', type=str)
    parser.add_argument('-o', '--outfile', help=outfile_help,
                        default=file_name_default, type=str)
    parser.add_argument('-p', '--path', help=path_help,
                        default=path_default, type=str)
    args = parser.parse_args()
    return args.domain, args.outfile, args.path


def find_first_dot_of(arg) -> int:
    '''
    :aim: this function takes a domain address and gives first dot number of it:
    :param: domain:
    :returns:       int: index number of first period: 
    '''
    return lambda: re.search(r'\.', arg).start()


def check_domain(domain: str) -> bool:
    '''
    :params:        a domain name that typed a user:
    '''
    schemes = ['http:\\www', 'www', 'https:\\www', 'http']

    if domain[:find_first_dot_of(domain)()] in schemes:
        return True


def check_file_name(file_name: str, domain: str, path: str) -> str:
    if file_name == 'file_name':
        new_file_name = create_file_name(domain)
        while os.path.exists(merge_paths([path, new_file_name])):
            new_file_name = new_file_name[:-9] + '[' + \
                str(int(new_file_name[-8:-5]) + 10) + '].txt'
        return new_file_name
    elif not file_name.endswith('.txt'):
        return '.'.join([file_name, '.txt'])
    else:
        return file_name


def create_file_name(domain_name: str):
    '''
    :aim: It takes the domain and creates a filename associated with it:
    :param: str: domain_name: 
    '''
    return ''.join(['doms_of_', domain_name, '[100].txt'])


def main() -> None:
    '''
    :params :   no param:
    :returns:   None:
    :aim    :   run the program:
    '''
    domain, file_name, path = user_args_fun()
    pars_1 = ParseHand(domain)
    domain = pars_1.network_1.domain
    file_name = check_file_name(file_name, domain, path)
    first_dot_index_number = find_first_dot_of(domain)()
    result_set = pars_1.saperate_texts(domain[first_dot_index_number:])
    file_1 = FileHand(path, file_name, result_set)
    file_1.write_file()


if __name__ == '__main__':

    main()