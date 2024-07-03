class SyntaxAnalyzer:
    def __init__(self):
        self.tokens = []
        self.lexemes = []
        self.current = '' 
        self.index = -1
        self.table = {
            0: {'N': ('s', 3), '+': 'error', '-': 'error', '*': 'error', '/': 'error', '$': 'error', 'E': 1, 'T': 2},
            1: {'N': 'error', '+': ('s', 4), '-': ('s', 5), '*': 'error', '/': 'error', '$': 'acc', 'E': 'error', 'T': 'error'},
            2: {'N': 'error', '+': ('r', 3), '-': ('r', 3), '*': ('s', 6), '/': ('s', 7), '$': ('r', 3), 'E': 'error', 'T': 'error'},
            3: {'N': ('r', 6), '+': ('r', 6), '-': ('r', 6), '*': ('r', 6), '/': ('r', 6), '$': ('r', 6), 'E': 'error', 'T': 'error'},
            4: {'N': ('s', 3), '+': 'error', '-': 'error', '*': 'error', '/': 'error', '$': 'error', 'E': 'error', 'T': 8},
            5: {'N': ('s', 3), '+': 'error', '-': 'error', '*': 'error', '/': 'error', '$': 'error', 'E': 'error', 'T': 9},
            6: {'N': ('s', 10), '+': 'error', '-': 'error', '*': 'error', '/': 'error', '$': 'error', 'E': 'error', 'T': 'error'},
            7: {'N': ('s', 11), '+': 'error', '-': 'error', '*': 'error', '/': 'error', '$': 'error', 'E': 'error', 'T': 'error'},
            8: {'N': 'error', '+': ('r', 1), '-': ('r', 1), '*': ('s', 6), '/': ('s', 7), '$': ('r', 1), 'E': 'error', 'T': 'error'},
            9: {'N': 'error', '+': ('r', 2), '-': ('r', 2), '*': ('s', 6), '/': ('s', 7), '$': ('r', 2), 'E': 'error', 'T': 'error'},
            10: {'N': ('r', 4), '+': ('r', 4), '-': ('r', 4), '*': ('r', 4), '/': ('r', 4), '$': ('r', 4), 'E': 'error', 'T': 'error'},
            11: {'N': ('r', 5), '+': ('r', 5), '-': ('r', 5), '*': ('r', 5), '/': ('r', 5), '$': ('r', 5), 'E': 'error', 'T': 'error'},
        } # Shifted Reduced에서 사용될 parsing table
        # 구성은 직접 구성했던 파싱테이블을 LLM에게 제공하여 딕셔너리 형태로 만들기를 요청했다. 

        self.rules = {
            0: ('E\'', 2),
            1: ('E', 6),
            2: ('E', 6),
            3: ('E', 2),
            4: ('T', 6),
            5: ('T', 6),
            6: ('T', 2),
        } # 두 번째 값은 reduce 될 때 stack에서 pop될 요소의 개수
        


    def next_token(self):
        self.index += 1
        if self.tokens[self.index] != None : # 주어진 token의 마지막을 확인
            self.current = self.tokens[self.index] 
        else:
            self.current = None # 만약 이전 토큰이 마지막이었다면 그냥 None 반환


    def lexer(self, input):
        numberlist ='0123456789' 
        # 숫자인지를 확인하기 위해 리스트를 만든다. 
        # char.isdigit()과 같은 기능을 하는 셈. string 관련한 함수를 쓸 수 없기 때문에...
        
        for char in input: 
            if char in numberlist:
                self.current += char # 숫자가 두 자리 이상일 경우에는 모든 숫자를 다 current에 넣어준다
            else:
                if self.current: 
                    # char에 연산자들이 나오고, current에 숫자가 있을 경우 
                    # current의 내용들을 lexemes, token에 넣어준다
                    # current를 확인하는 이유는 ()+처럼 연산자 뒤에 연산자가 나올 수 있기 때문에
                    self.lexemes.append(self.current)
                    self.tokens.append('N')  
                    self.current = ''
                    # 다음 숫자들을 위해 current를 초기화 시켜준다
                self.lexemes.append(char)
                self.tokens.append(char)  # for문을 통해 들어온 char가 

        if self.current: # 마지막 숫자
            self.lexemes.append(self.current)
            self.tokens.append('N')

        self.lexemes.append('$')
        self.tokens.append('$')  # 입력 종료 심볼
        return self.lexemes, self.tokens
    
    def trace(self, step, action, stack, input_tokens): 
        # 출력 형태를 예시와 맞추기 위해 LLM에 명세에 주어진 예시를 넣고 코드를 요청하였다
        stack_str = ' '.join(map(str, stack))
        input_str = ' '.join(input_tokens[self.index:])
        action_str = action
        if isinstance(action, tuple):
            action_str = f"{'Shift' if action[0] == 's' else 'Reduce'} {action[1]}"
        print(f"({step:02}) |{stack_str:22} |{input_str:20} | {action_str:15} |")
        

    def production(self, number, values): 
        # 실제 값을 연산하기 위한 method
        # 인자로 들어오는 value 값은 string이어서 숫자형으로 바꿔야 한다
        # 이 때 주의해야 할 것은 int가 아니라 float로. 그렇지 않으면 결과 값이 바뀔 수도 있다. 
        if number == 1:  # E -> E + T
            return float(values[0]) + float(values[2])
        elif number == 2:  # E -> E - T
            return float(values[0]) - float(values[2])
        elif number == 3:  # E -> T
            return float(values[0])
        elif number == 4:  # T -> T * N
            return float(values[0]) * float(values[2])
        elif number == 5:  # T -> T / N
            return float(values[0]) / float(values[2])
        elif number == 6:  # T -> N
            return float(values[0])
        return None

    def SRL_parser(self, input_lexemes, input_tokens):
        self.tokens = input_tokens # lexer가 만든 tokens
        self.lexemes = input_lexemes
        self.current = ''
        self.index = -1
        stack = [0]
        values = []
        step = 0
        
        self.next_token()

        print("Tracing Start!!")
        print("+----------------------------+---------------------------------------+")
        print("|Step|          Stack        |         Input       |    Action       |")
        print("+----+-----------------------+---------------------------------------+")
        
        while True:
            top_state = stack[-1] #stack을 top에 위치한 state를 갖고 온다
            action = self.table[top_state].get(self.current, 'error') 
            # top_state와 input의 제일 첫 토큰(self.current)를 인자로 딕셔너리에서 action을 갖고 온다. 
            self.trace(step, action, stack, self.tokens) #for print
            
            if isinstance(action, tuple) and action[0] == 's':
                #action에서 갖고 온 튜플의 첫 번째 인자가 's'라면 shift
                stack.append(self.current) #stack에 현재 token을 넣어준다 
                stack.append(action[1]) #stack에 Shift x 명령에 따른 x 값을 넣어준다
                values.append(self.lexemes[self.index]) # 실제 연산을 위한 값도 넣어준다 
                self.next_token() # 그 다음 token을 확인한다
                self.current = self.tokens[self.index] # 이 부분은 next_token()으로 되어야 하나 오류가 발생해 따로 처리해주었다
    
            elif isinstance(action, tuple) and action[0] == 'r':
                #action에서 갖고 온 튜플의 첫 번째 인자가 'r이라면 Reduce
                rule_num = action[1] # 어떤 rule을 적용할 건지 두 번째 요소를 갖고 온다. 
                nonterminal, pop_count = self.rules[rule_num] #self.rule table에서 number에 해당하는 nonterminal, 감소시킬 요소의 숫자를 갖고온다 

                for i in range(pop_count):
                    stack.pop()
                # 주어진 숫자만큼 stack에서 pop한다. (array에서는 뒤에서부터 pop)

                reduced_values = values[-(pop_count // 2):] # 규칙의 오른쪽에 해당하는 값 검색
                values = values[:-(pop_count // 2)] #팝할 값 수 계산 
                
                # reduce 과정을 마친 뒤, goto state를 계산한다 
                top_state = stack[-1] 
                goto_state = self.table[top_state][nonterminal] # goto state를 계산해준다 
                stack.append(nonterminal) 
                stack.append(goto_state)

                # 최종 결과값을 계산하기 위해 reduce했던 rule의 번호와 해당 값을 produciton method로 보냄
                result = self.production(rule_num, reduced_values) 
                values.append(result)

            elif action == 'acc':
                print("")
                print("Parsing success!")
                print("")
                print(f"Result: {values[0]}")
                break
            elif action == "error":
                print("Syntax error")
                break
            
            step += 1
        

            





    def RD_parser(self, input_lexemes, input_tokens):
        self.tokens = input_tokens # lexer가 만든 token
        self.lexemes = input_lexemes # lexer가 만든 lexeme
        self.current = '' #lexer에서 썼으므로, 초기화 시켜준다
        self.index = -1
        self.next_token() # 현재 current를 설정하여 시작해준다. 
        
        print("LET'S START!")
        return self.E()

    def E(self):
        print("Enter E")
        value = self.T() #T를 호출하고, T가 N을 호출해 받아온 숫자를 넣어준다
        result = self.E_prime(value) 
        # 만약 T를 호출해서 *, /가 아니어서 
        # operator의 앞 operand만 그대로 갖고 오게 된다면(inherited value) +,-로 넘어가게 된다.
        # 해당 숫자를 가지고 E' 함수를 호출한다 
        print("Exit E")
        return result

    def E_prime(self, inherited_value):
        print("Enter E'")
        if self.current == '+': # 모든 과정은 T_prime 내에 있는 * 과정과 동일하다.
            self.next_token()
            value = self.T() 
            # 그러나 E'은 T'를 먼저 수행한 후 그 값을 받아온다.
            # */이 +-보다 priority가 있기 때문이다 
            result = self.E_prime(inherited_value + value)
            print("Exit E'")
            return result 
        elif self.current == '-': #+와 동일하다 
            self.next_token()
            value = self.T()
            result = self.E_prime(inherited_value - value)
            print("Exit E'")
            return result 
        else:
            print("epsilon")
            print("Exit E'")
            return inherited_value

    def T(self):
        print("Enter T")
        value = self.N() # N을 호출해 숫자를 받아온다. 
        result = self.T_prime(value) #받아온 숫자로 T'를 호출한다. 
        print("Exit T")
        return result #T를 호출하는 것은 E밖에 없으므로, E 내로 반환된다

    def T_prime(self, inherited_value):
        print("Enter T'")
        if self.current== '*': #N을 호출하고 난 뒤 current가 operator로 바뀌었으므로 확인
            self.next_token() #operator 뒤의 숫자로 current를 조정한다. 
            value = self.N() #그리고 N을 호출하여 그 숫자를 정수형으로 받아온다 
            result = self.T_prime(inherited_value * value) 
            #inherited_value는 operator의 앞 operand, value는 operator의 뒤 operand
            print("Exit T'")
            return result
        elif self.current == '/': #*r과 동일한 로직이다 
            self.next_token() 
            value = self.N()
            result = self.T_prime(inherited_value / value)
            print("Exit T'")
            return result
        else: # 만약 *, /도 아니라면 grammar상으로는 앱실론. 
            print("epsilon")
            print("Exit T'")
            return inherited_value #별다른 과정 없이 받았던 argument를 그대로 반환한다. 

    def N(self):
        #print("what is that" + str(self.current))
        if self.current == 'N': #만약 token이 N이라면 숫자이므로,
            value = int(self.lexemes[self.index]) #string 형태일 숫자를 int 형변환 해준다
            self.next_token() # N 뒤의 operator를 current로 설정해준다. 
            #만약 ()가 있다면 이 부분에서 추가적인 판단이 있었겠지만, +-*/만 사용하므로
            #number -> operator -> number -> operator ...가 보장된다. 
        
            return value
        else:
            raise Exception("Syntax Error: Expected a number, got {}".format(self.current))



# 사용 예시
S = SyntaxAnalyzer()
lexemes, tokens = S.lexer(input())
print("#1")
print("")
print("Lexemes: " + str(lexemes))
print("Tokens: " + str(tokens))
print("")
print("----------------------------")
print("#2")
print("")
result1 = S.SRL_parser(lexemes, tokens)

print("----------------------------")
print("#3")
print("")
result2 = S.RD_parser(lexemes, tokens)
print("Recursive-Descent parsing Result: " + str(result2))


