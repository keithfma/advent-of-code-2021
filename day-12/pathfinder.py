import typing as T
import attr


START_NAME = 'start'
END_NAME = 'end'



class RevisitError(Exception):
    """Raise if a path tries to revisit a node it can only visit once"""



@attr.define
class Cave:

    name: str = attr.ib()
    nbrs: T.List['Cave'] = attr.ib(factory=list)

    def __attr_post_init__(self):
        if not (self.name.isupper() or self.name.islower()):
            raise ValueError('Mixed case name is not allowed!')

    @property
    def visit_once_only(self):
        return self.name.islower()

    def add_neighbor(self, other: 'Cave'):
        self.nbrs.append(other)

    def __repr__(self) -> str:
        nbrs_str = '["' + '", "'.join(x.name for x in self.nbrs) + '"]'
        return f'{self.__class__.__name__}("{self.name}", nbrs={nbrs_str})'


@attr.frozen
class Path:

    steps: T.Tuple['Cave'] = attr.ib()

    def __attr_post_init__(self):
        if not self.steps or self.steps[0].name != START_NAME:
            raise ValueError('Paths must begin at the starting cave')

    def add_step(self, step: 'Cave') -> 'Path':
        """Return a new Path with an extra last step"""

        if step in self.steps and step.visit_once_only:
            raise RevisitError(f'{self} cannot revisit {step}')

        return self.__class__((*self.steps, step)) 

    @property
    def complete(self):
        return self.steps[-1].name == END_NAME

    def __repr__(self) -> str:
        steps_str = '"' + '"->"'.join(x.name for x in self.steps) + '"'
        return f'{self.__class__.__name__}({steps_str})'



def parse_input(filename: str) -> T.Tuple[Cave, T.List[Cave], Cave]:
   # map name to cave object 
    objs = dict()
    
    with open(filename, 'r') as fp:
        for line in fp.readlines():
            
            names = line.strip().split('-')
            
            # create objects if needed
            for name in names:
                if name not in objs:
                    objs[name] = Cave(name)

            # create 2-way edge
            objs[names[0]].add_neighbor(objs[names[1]])
            objs[names[1]].add_neighbor(objs[names[0]])

    # munge and return
    start = objs[START_NAME]
    end = objs[END_NAME]
    objs = [x for x in objs.values() if x.name not in {START_NAME, END_NAME}]
    
    return start, objs, end



def count_unique_paths(start: Cave) -> int:

    complete_paths = 0 

    open_paths = [Path([start])]

    while open_paths:
    
        current_path = open_paths.pop()
        
        for next_step in current_path.steps[-1].nbrs:
            try: 
                new_path = current_path.add_step(next_step)
                if new_path.complete:
                    complete_paths += 1
                else:
                    open_paths.append(new_path)
            except RevisitError:
                pass

    return complete_paths

        
        
            
                        

if __name__ == '__main__':
    

    input_file = 'test_input_1.txt'
    input_file = 'test_input_2.txt'
    input_file = 'input.txt'

    start_cave, caves, end_cave = parse_input(input_file) 

    print('puzzle 1 ----------')
    print(f'Number of unique paths: {count_unique_paths(start_cave)}')
    print()



            
            




        
        
    
            
    
