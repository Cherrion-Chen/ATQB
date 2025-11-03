import pandas as pd

def avoid_repeat(l):
    l = list(map(str, l))
    num = {}

    for i in range(len(l)):
        try:
            num[l[i]] += 1
            l[i] = l[i] + '.' + str(num[l[i]]-1)
        except:
            num[l[i]] = 1
    
    return l

class Stud:
    '''
    Individual student object.
    Personal inofrmation can be storaged and operated throuth this.
    '''
    
    def __init__(self, id, info=['姓名'], aug=None):
        '''
        Attributes:
            id: student id
            info: name of the information you want to storage
            aug: augmented id prefix, which marks the class division information
            dct: a dictionary storaging all the information
        '''
        
        if aug is None: self.id = str(id)
        else: self.id = str(aug)+'@'+str(id)

        self.info = avoid_repeat(info)
        self.aug = aug

        self.dct = dict.fromkeys(['学号']+info, pd.NA)
        self.dct['学号'] = id
    
    def __getitem__(self, name):
        '''
        Get the value of specified information.
        
        Input: name of the required information
        Output: value of the corresponding information
        '''
        
        if isinstance(name, list):
            return [self.dct[i] for i in name]
        return self.dct[name]
    
    def __setitem__(self, index, value):
        '''
        Modify value of the information.
        
        Input: name and new value of the information which you want to modify
        Output: new value of the corresponding information
        '''
        
        if isinstance(index, list):
            if len(index) != len(value):
                raise ValueError('List index and List value should have same length.')
            
            for i in range(len(index)):
                try: self.dct[index[i]]
                except: raise KeyError('Out of index.')
                self.dct[index[i]] = value[i]
            return
        
        try: self.dct[index]
        except: raise KeyError('Out of index.')
        self.dct[index] = value

    def append(self, info, value):
        '''
        Add information to the student.
        
        Input: name and value of the information which you want to revise
        Output: none
        '''
        
        if info in self.info:
            raise ValueError(f'Information {info} repeated.')
        self.info.append(info)
        self.dct[info] = value

    def rename_info(self, infor, new):
        '''
        Rename specified information.
        
        Input: name of the information which you want to rename
        Output: none
        '''
        self.info[self.info.index(infor)] = new

    def pop(self, info):
        '''
        Delete information.
        
        Input: name of the information which you want to delete
        Output: value of the corresponding information
        '''
        op = self[info]
        self.info.remove(info)
        self.dct.pop(info)
        return op
    
    def items(self):
        return self.dct.items()
    
    def values(self):
        '''
        List of the information value
        '''
        return list(self.dct.values())[1:]
    
    def __list__(self):
        return self.dct.items()
    
    def __iter__(self):
        return iter(self.dct.items())
    
    def __str__(self):
        l1 = '\t'.join(list(map(str, self.dct.keys())))
        l2 = '\t'.join(list(map(str, self.dct.values())))
        return l1 + '\n' + l2
    
    def copy(self):
        '''
        Copy a Stud object that is independent of the original one.
        '''
        
        op = Stud(self.id, [i for i in self.info], self.aug)
        op[op.info] = self.values()
        return op
    
class StudFrame:
    '''
    Frame of students.
    Information can be storaged and operated with this.
    Provide easy conversion to DataFrame objects and Excel Files.
    '''
    
    def __init__(self, info=['姓名'], aug=None):
        '''
        Attributes
            info: name of the information you want to storage
            aug: augmented id prefix, which marks the class division information
            studs: 2D List, storages ID and information of students
        '''
        
        self.info = [i for i in info]
        self.aug = aug
        self.studs = []  # Storages ID and values only.

    def load(self, studs: list[Stud]):
        '''
        Get information from list of Stud objects.
        
        Input: list of Stud objects
        Output: None
        '''
        
        self.info = studs[0].info
        self.aug = studs[0].aug
        self.studs = [[i.id] + i.values() for i in studs]

    def from_df(self, df: pd.DataFrame, aug=None):
        '''
        Get information from DataFrame object.
        
        Input: list of Stud objects
        Output: None
        '''
        
        self.info = avoid_repeat(list(df.columns[1:]))
        self.aug = aug
        self.studs = [list(df.iloc[i]) for i in range(len(df))]
        self.operate_column('学号', str)

    def from_excel(self, path: str):
        '''
        Get information from Excel File.
        
        Input: path of the Excel File
        Output: None
        '''
        df = pd.read_excel(path)
        self.from_df(df)

    def to_df(self):
        '''
        Write information into DataFrame.
        
        Input: None
        Output: DataFrame Object
        '''
        return pd.DataFrame(self.studs, columns=['学号']+self.info)
    
    def to_excel(self, path='./标准输出.xlsx'):
        '''
        Write information into Excel File.
        
        Input: path of the Excel File
        Output: None
        '''
        self.to_df().to_excel(path, index=False)

    def id_list(self):
        return [i[0] for i in self.studs]

    def __getitem__(self, index):
        '''
        Get information of an individual student.
        Support list of indexes.
        
        Input: index of the student in the Student Frame
        Output: Stud object
        '''
        
        if isinstance(index, list):
            op = StudFrame(self.info,self.aug)

            for i in index:
                op.studs.append([v for v in self.studs[i]])
            return op
            
        stu = Stud(self.studs[index][0], self.info, self.aug)
        stu[stu.info] = [v for v in self.studs[index][1:]]
        return stu
    
    def __setitem__(self, index, value):
        '''
        Modify information of an individual student.
        Support list of indexes and values.
        
        Input: index and new value of the student in the Student Frame
        Output: None
        '''
        
        if isinstance(index, list):
            if len(index) != len(value):
                raise ValueError('List index and List value should have same length.')
            
            for i in range(len(index)):
                self.studs[index[i]] = [value[i].id] + value[i].values()
            
            return
        
        self[index] = value
        
    def set_info(self, id: str, info_name, value):
        '''
        Modify specified information of specified student.
        
        Input:
            id: ID of the student
            info_name: name of the information
            value: new value of the information
        '''
        
        ind = self.id_list().index(id)
        if info_name is None or info_name=='学号':
            col = 0
        else: col = self.info.index(info_name)+1
        
        self.studs[ind][col] = value

    def rename_info(self, infor, new):
        '''
        Rename specified information
        
        Input: name of the information which you want to rename
        Output: none
        '''
        self.info[self.info.index(infor)] = new

    def find_id(self, id):
        '''
        Get information of the individual student with the specified ID.
        
        Input: ID of the student
        Output: Stud object
        '''
        
        ind = self.id_list().index(id)
        return self[ind]

    def append(self, x):
        '''
        Add new students to the Student Frame.
        Support list of new students
        
        Input: Stud objects
        Output: None
        '''
        
        if not isinstance(x, list):
            x = [x]

        for stu in x:
            arr = []
            for i in self.info:
                try: arr.append(stu[i])
                except: arr.append(pd.NA)

            self.studs.append([stu.id]+arr)

    def pop(self, id):
        '''
        Delete the individual student with the specified ID.
        
        Input: ID of the student
        Output: None
        '''
        
        index = self.id_list().index(id)
        op = self[index]
        self.studs.pop[index]
        return op
    
    def remove_info(self, info_name):
        '''
        Delete the information with specified name.
        
        Input: ID of the student
        Output: None
        '''
        
        i = self.info.index(info_name)
        self.info.pop(i)

        for r in range(len(self)):
            self.studs[r].pop(i+1)

    def __len__(self):
        return len(self.studs)
    
    def __iter__(self):
        return iter([self[i] for i in range(len(self))])

    def __str__(self):
        op = ['\t'.join(['学号']+list(map(str, self.info)))]
        op = op + ['\t'.join(list(map(str, i))) for i in self.studs]
        return '\n'.join(op)
    
    def copy(self):
        '''
        Copy a StudFrame object that is independent of the original one.
        '''
        
        op = StudFrame([i for i in self.info], self.aug)
        op.studs = [[i for i in row] for row in self.studs]
        return op
    
    def select(self, info_name):
        '''
        Select specified information and get a new Student Frame.
        Support list of information names.
        
        Input: name of the information
        Output: StudFrame object
        '''
        
        op = StudFrame(info_name, self.aug)
        inds = [0] + [self.info.index(i)+1 for i in info_name]

        for i in range(len(self)):
            op.studs.append([self.studs[i][j] for j in inds])
        
        return op
    
    def map(self, func, other_args=None, info_name='Result', retain=['姓名']):
        '''
        Exert a function to all students and get a new student frame.
        
        Input:
            func: must be like func(stu:Stud) or func(stu:Stud, other_args: Any)
            other_args: auxiliary argument of func (if there is)
            info_name: name of the new information
            retain: names of the information you want the new frame to inherit
        Output: StudFrame object
        '''
        
        if retain == 'all':
            retain = [i for i in self.info]
        if not isinstance(retain, list):
            retain = [retain]
        
        op = self.select(retain)
        op.info.append(info_name)

        for i in range(len(self)):
            new_info = func(self[i]) if other_args is None else func(self[i], other_args)
            op.studs[i].append(new_info)
        
        return op
    
    def operate_column(self, info_name, func):
        '''
        Exert a function to specified column.
        
        Input:
            info_name: name of the new information
            func: must be like func(x)
        Output:None
        '''
        
        if info_name=='学号' or info_name is None:
            ind = 0
        else:
            ind = self.info.index(info_name)+1

        for i in range(len(self)):
            self.studs[i][ind] = func(self.studs[i][ind])
            
    def drpona(self, info_names='all', how='all'):
        '''
        Delete individual students with vacant value.
        
        Input:
            info_names: vacant value in these information names
            how: delete when all or any of the values are vacant
        '''
        if info_names == 'all':
            info_names = list(range(1, len(self.info)+1))
        elif isinstance(info_names, list):
            info_names = [self.info.index(i)+1 for i in info_names]
        else:
            info_names = [self.info.index(info_names)+1]

        r = 0
        while r < len(self):
            na = [pd.isna(self.studs[r][i]) for i in info_names]
            how = all if how=='all' else any
            na = how(na)
        
            if na: self.studs.pop(r)
            else: r += 1
