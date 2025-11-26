from manim import *
import numpy as np

class VirtualMemoryAnimation(Scene):
    def construct(self):
        # Colors
        self.OS_COLOR = PURPLE
        self.CLOCK_COLOR = WHITE
        
        # Font sizes
        self.CODE_FONT_SIZE = 20
        self.MEMORY_FONT_SIZE = 18
        self.API_FONT_SIZE = 16
        
        # Create main groups with proper positioning
        code_group = VGroup()
        self.dasm_group = VGroup()
        os_group = VGroup()
        stack_group = VGroup()
        heap_group = VGroup()
        function_group = VGroup()
        
        # 1. Code block (LEFT side - centered vertically)
        code_lines = [
            "int main() {",
            "    int* ptr = new int;",
            "    *ptr = 42;", 
            "    delete ptr;",
            "}"
        ]


        dasm_lines = [
            "mov rax, [rsp + addr_ptr]",
            "mov [rax], 42"
        ]

        code_block = VGroup(*[
            Text(line, font_size=self.CODE_FONT_SIZE, font="Monospace") 
            for line in code_lines
        ]).arrange(DOWN, aligned_edge=LEFT)
        
        code_rect = SurroundingRectangle(
            code_block, 
            color=WHITE, 
            buff=0.3,
            stroke_width=2
        )
        code_title = Text("Код программы", font_size=22).next_to(code_rect, UP, buff=0.2)
        code_group.add(code_title, code_rect, code_block)
        code_group.move_to(LEFT * 5)  # Move to left side

        dasm_block = VGroup(*[
            Text(line, font_size=self.CODE_FONT_SIZE, font="Monospace") 
            for line in dasm_lines
        ]).arrange(DOWN, aligned_edge=LEFT)
        
        dasm_code_rect = SurroundingRectangle(
            dasm_block, 
            color=WHITE, 
            buff=0.2,
            stroke_width=1.5
        )
        dasm_title = Text("Дизассемблированный код", font_size=18).next_to(dasm_code_rect, UP, buff=0.2)
        self.dasm_group.add(dasm_title, dasm_code_rect, dasm_block)
        self.dasm_group.move_to(LEFT*3 + DOWN*2.8)  # Move to left side


               
        # 2. OS Block (TOP CENTER)
        os_rect = Rectangle(width=3.5, height=1.5, color=self.OS_COLOR, stroke_width=2)
        os_title = Text("Операционная Система", font_size=20).next_to(os_rect, UP, buff=0.2)
        
        # WinAPI functions
        api_functions = ["VirtualAlloc()", "HeapAlloc()", "VirtualFree()"]
        self.api_texts = VGroup(*[
            Text(func, font_size=self.API_FONT_SIZE, font="Monospace")
            for func in api_functions
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        self.api_texts.move_to(os_rect.get_left() + RIGHT*1.3)
        
        # Clock INSIDE OS rectangle
        clock_circle = Circle(radius=0.2, color=self.CLOCK_COLOR, stroke_width=2)
        clock_center = clock_circle.get_center()
        clock_hand = Line(clock_center, clock_center + UP * 0.12, color=self.CLOCK_COLOR, stroke_width=2)
        clock_group = VGroup(clock_circle, clock_hand)
        clock_group.move_to(os_rect.get_right() + LEFT*0.5)
        
        os_group.add(os_title, os_rect, self.api_texts, clock_group)
        os_group.move_to(UP * 2.5)  # Top center
        
        # 3. Stack Memory (TOP RIGHT) READY!!!
        stack_rect = Rectangle(width=4.5, height=2.75, color=BLUE, stroke_width=2)
        stack_title = Text("Стек", font_size=20).next_to(stack_rect, UP, buff=0.2)

        stack_data = [
            ("0x7ffd1234", "main()"),
            ("0x7ffd1230", "0x00000000"),
            ("0x7ffd122c", "0xdddddddd"),
            ("0x7ffd1228", "0xffffffff"),
            ("0x7ffd1224", "0x00000000")
        ]

        self.stack_lines = VGroup()
        for addr, data in stack_data:
            # Create background block for each stack entry
            block_bg = Rectangle(
                width=2.4, height=0.4, 
                stroke_color=BLUE,
                stroke_width=1
            ).move_to(stack_rect.get_center() + RIGHT*0.1)
            addr_text = Text(addr, font_size=self.MEMORY_FONT_SIZE-1, font="Monospace")
            data_text = Text(data, font_size=self.MEMORY_FONT_SIZE-2, font="Monospace", color=LIGHT_GRAY)
            addr_text.move_to(stack_rect.get_left())
            data_text.move_to(block_bg.get_center())  # Moved more right
            
            line_group = VGroup(block_bg, addr_text, data_text)
            self.stack_lines.add(line_group)
        self.stack_lines.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        self.stack_lines.move_to(stack_rect.get_center())
        
        stack_group.add(stack_title, stack_rect, self.stack_lines)
        stack_group.move_to(RIGHT * 4.7 + UP * 1.8)  # Top right
        
        # 4. Heap Memory (BOTTOM RIGHT)
        heap_rect = Rectangle(width=4.5, height=2.75, color=GREEN, stroke_width=2)
        heap_title = Text("Динамическая память", font_size=20).next_to(heap_rect, UP, buff=0.2)
        page_info = Text("Размер страницы: 4096 байт", font_size=12, color=GRAY)
        page_info.next_to(heap_title, UP, buff=0.1)
        # Heap addresses (different range - low addresses)
        heap_data = [
            ("0x55a11000", "[занято 2048 байт]"),
            ("0x55a12000","[занято 3072 байт]"),
            ("0x55a13000", "[занято 0 байт]"),
            ("0x55a14000", "[занято 1024 байт]"),
            ("0x55a15000", "[занято 4078 байт]")
        ]
        self.heap_data_texts = []
        self.heap_lines = VGroup()
        for addr,data in heap_data:
            block_hp = Rectangle(
                width=2.7, height=0.4, 
                stroke_color=BLUE,
                stroke_width=1
            ).move_to(heap_rect.get_center() + RIGHT*0.1)
            hp_addr_text = Text(addr, font_size=self.MEMORY_FONT_SIZE-1, font="Monospace")
            hp_data_text = Text(data, font_size=self.MEMORY_FONT_SIZE-2, font="Monospace", color=LIGHT_GRAY)
            hp_addr_text.move_to(heap_rect.get_left())
            hp_data_text.move_to(block_hp.get_center())

            hp_line_group = VGroup(block_hp, hp_addr_text, hp_data_text)
            self.heap_lines.add(hp_line_group)
            self.heap_data_texts.append(hp_data_text)
        self.heap_lines.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        self.heap_lines.move_to(heap_rect.get_center())
        
        heap_group.add(heap_title, heap_rect, self.heap_lines, page_info)
        heap_group.move_to(RIGHT * 4.7 + DOWN * 1.8)  # Bottom right
        
        # 5. Function block (CENTER - между кодом и памятью)
        func_rect = Rectangle(width=1.2, height=0.3, color=BLACK, stroke_width=1)
        func_title = Text("Функция C", font_size=18).next_to(func_rect, UP, buff=0.2)
        
        self.malloc_text = Text("malloc()", font_size=20, font="Monospace", color=GREEN)
        self.free_text = Text("free()", font_size=20, font="Monospace", color=RED)
        
        function_group.add(func_title, func_rect).move_to(LEFT*3 + UP*2.5)
          # Center position
        
        # Create all static elements with proper positioning
        self.play(
            LaggedStart(
                Create(code_group),
                Create(os_group),
                Create(stack_group),
                Create(heap_group),
                lag_ratio=0.3
            ),
            run_time=3
        )
        
        self.wait(1)
        
        # Store references for animation sequences
        self.code_block = code_block
        self.function_group = function_group
        self.os_group = os_group
        self.clock_hand = clock_hand
        self.heap_group = heap_group
        
        # Animation sequences
        self.show_malloc_sequence()
        self.show_assignment_sequence()
        # self.show_free_sequence()
    
    def show_malloc_sequence(self):
        """Animate memory allocation sequence"""
        # ВЫДЕЛЯЕМ ПЕРВУЮ СТРОКУ КОДА
        API_HIGHLIGHT = YELLOW
        # Highlight "new int" line
        new_line = self.code_block[1]  # "    int* ptr = new int;"
        highlight_rect = SurroundingRectangle(new_line, color=YELLOW, buff=0.1, stroke_width=3)
        
        self.play(Create(highlight_rect), run_time=1)
        self.wait(0.5)

        func_rect = self.function_group[1]
        self.malloc_text.move_to(func_rect.get_center())

        arrow_start = highlight_rect.get_right()
        arrow_end = func_rect.get_bottom()
        func_arrow = Arrow(arrow_start, arrow_end, color=YELLOW, buff=0.1, stroke_width=2)
        
        
        # СТРЕЛКА ДО ФУНКЦИИ С И ПОЯВЛЕНИЕ MALLOC
        self.play(
            Create(func_arrow),
            Create(self.function_group),
            Write(self.malloc_text), 
            run_time=1
        )

        self.wait(0.5)    
        
        
        
       

        # ВЫДЕЛЯЕМ VIRTUALALLOC И СТРЕЛКА ДО НЕГО ОТ MALLOC()
        heapalloc_highlight = SurroundingRectangle(
            self.api_texts[0], 
            color=API_HIGHLIGHT, 
            buff=0.1, 
            stroke_width=3
        )

        self.old_heap_high = heapalloc_highlight

        arrow_start = func_rect.get_right()
        arrow_end = heapalloc_highlight.get_left()
        func1_arrow = Arrow(arrow_start, arrow_end, color=YELLOW, buff=0.1, stroke_width=2)
        
        self.play(Create(func1_arrow), run_time=1)
        self.wait(0.5)
        
        self.play(Create(heapalloc_highlight), run_time=1)
        self.wait(0.5)

        # ЗАДАЕТСЯ УКАЗАТЕЛЬ ДИН. ПАМЯТИ НА ПЕРВОЙ ЕЁ СТРОЧКЕ
        pointer_triangle = Triangle(
            color=YELLOW, 
            fill_opacity=1, 
            stroke_width=2
        ).scale(0.08)
        pointer_triangle.rotate(-90 * DEGREES)

        first_heap_block = self.heap_lines[0]
        pointer_triangle.move_to(first_heap_block.get_left() + LEFT * 0.2)

        self.play(Create(pointer_triangle), run_time=0.5)
        self.wait(0.5)

        blocks_to_search = [0, 1, 2]  # First three blocks

        self.play(
            FadeOut(func_arrow),
            FadeOut(func1_arrow)
        )

        # ДВИЖЕНИЕ УКАЗАТЕЛЯ И ПОИСК ПОДХОДЯЩЕГО БЛОКА
        
        for i, block_idx in enumerate(blocks_to_search):
            current_block = self.heap_lines[block_idx]
            
            # Move pointer to current block
            pointer_target = current_block.get_left() + LEFT * 0.2
            self.play(
                pointer_triangle.animate.move_to(pointer_target),
                run_time=0.8
            )
            # Animate clock
            self.animate_clock()
            
            if i < 2:  # First two blocks - not enough memory
                # Show why it doesn't fit
                error_rect = SurroundingRectangle(current_block, buff=0.05, stroke_width=3).set_color(RED)
                
                # Create background for reason text
                reason_bg = Rectangle(
                    width=2.5, height=0.4,
                    fill_color=BLACK,
                    fill_opacity=1,
                    stroke_color=RED,
                    stroke_width=1
                )
                reason_text = Text("Мало свободного места!", font_size=12, color=RED)
                reason_group = VGroup(reason_bg, reason_text)
                reason_group.next_to(current_block, UP, buff=0.1)
                
                self.play(
                    Create(error_rect),
                    Create(reason_group),
                    run_time=0.8
                )
                self.wait(0.5)
                self.play(
                    FadeOut(error_rect),
                    FadeOut(reason_group),
                    run_time=0.3
                )
            else:  # Third block - suitable
                success_rect = SurroundingRectangle(
                    current_block, 
                    color=GREEN, 
                    buff=0.05, 
                    stroke_width=4
                )
                
                reserved_bg = Rectangle(
                    width=2.2, height=0.4,
                    fill_color=BLACK,
                    fill_opacity=0.9,
                    stroke_color=GREEN,
                    stroke_width=1
                )
                reserved_text = Text(
                    "Блок зарезервирован", 
                    font_size=11, 
                    color=GREEN
                )
                reserved_group = VGroup(reserved_bg, reserved_text)
                reserved_group.next_to(current_block, UP, buff=0.1)
                
                self.play(
                    Create(success_rect),
                    Create(reserved_group),
                    run_time=1
                )
                
                # Store references for later use
                self.allocated_block_rect = success_rect
                self.reserved_group = reserved_group
                self.allocated_block_index = block_idx               
                
                self.wait(1)
            
            
            
            # Keep the highlight
            self.current_highlight = highlight_rect


        arrow_start = self.allocated_block_rect.get_left()
        arrow_end = self.os_group.get_bottom()
        func_back2_arrow = Arrow(arrow_start, arrow_end, color=YELLOW, buff=0.1, stroke_width=2)
        
        self.play(Create(func_back2_arrow), run_time=1)
        self.wait(0.5)
        
        arrow_end = func_rect.get_right()
        arrow_start = heapalloc_highlight.get_left()
        func_back_arrow = Arrow(arrow_start, arrow_end, color=YELLOW, buff=0.1, stroke_width=2)
        
        self.play(Create(func_back_arrow), run_time=1)
        self.wait(0.5)

        arrow_end = highlight_rect.get_right()
        arrow_start = func_rect.get_bottom()
        func_back1_arrow = Arrow(arrow_start, arrow_end, color=YELLOW, buff=0.1, stroke_width=2)
        
        self.play(Create(func_back1_arrow), run_time=1)
        self.wait(0.5)
        
         # ЗАПИСЫВАЕМ УКАЗАТЕЛЬ В СТЕК
        self.update_stack_with_pointer("0x55a13000")

        self.play(
            FadeOut(func_back_arrow),
            FadeOut(func_back1_arrow),
            FadeOut(func_back2_arrow),
            FadeOut(self.function_group),
            FadeOut(self.malloc_text),
            run_time=1
        )

        self.wait(0.5)


    def update_stack_with_pointer(self, pointer_address):
        """Update stack with the allocated pointer"""
        # Находим строку стека для записи указателя (вторая строка - 0x7ffd1230)
        stack_entry = self.stack_lines[1]  # Вторая строка стека
        old_data_text = stack_entry[2]  # Третий элемент - текстовое поле с данными

        
        
        # Создаем новый текст с указателем
        new_data_text = Text(f"ptr={pointer_address}", 
                            font_size=self.MEMORY_FONT_SIZE-2, 
                            font="Monospace", 
                            color=YELLOW)
        new_data_text.move_to(old_data_text.get_center())
        
        # Анимируем изменение
        self.play(
            Transform(old_data_text, new_data_text),
            run_time=1
        )
        
        # Обновляем ссылку
        stack_entry.remove(old_data_text)
        stack_entry.add(new_data_text)

    def show_assignment_sequence(self):
        """Animate variable assignment sequence"""
        self.wait(1)

        self.play(
             Create(self.dasm_group),
             run_time=1
        )
        
        # Highlight assignment line
        assignment_line = self.code_block[2]  # "    *ptr = 42;"
        new_highlight = SurroundingRectangle(
            assignment_line, 
            color=YELLOW, 
            buff=0.1, 
            stroke_width=3
        )
        
        heapalloc_highlight = SurroundingRectangle(
            self.api_texts[1], 
            color=YELLOW, 
            buff=0.1, 
            stroke_width=3
        )

        self.play(
            Transform(self.current_highlight, new_highlight),
            Transform(self.old_heap_high, heapalloc_highlight),
            run_time=1
        )
        self.wait(0.5)
        
        arrow_start = new_highlight.get_right()
        arrow_end = self.dasm_group.get_top()
        dasm1_arrow = Arrow(arrow_start, arrow_end, color=YELLOW, buff=0.1, stroke_width=2)
        
        self.play(Create(dasm1_arrow), run_time=1)
        self.wait(0.5)


        
        # Записываем значение в кучу
        allocated_block_group = self.heap_lines[self.allocated_block_index]
        old_data_text = allocated_block_group[2]

        arrow_start = self.dasm_group.get_right()
        arrow_end = allocated_block_group.get_left()
        dasm2_arrow = Arrow(arrow_start, arrow_end, color=YELLOW, buff=0.1, stroke_width=2)
        
        self.play(Create(dasm2_arrow), run_time=1)
        self.wait(0.5)
        
        new_data_text = Text("42", font_size=self.MEMORY_FONT_SIZE-2, font="Monospace", color=YELLOW)
        new_data_text.move_to(old_data_text.get_center())
        
        # Анимация записи значения
        self.play(
            Transform(old_data_text, new_data_text),
            run_time=1
        )
        
        # Обновляем ссылку
        allocated_block_group.remove(old_data_text)
        allocated_block_group.add(new_data_text)
        
        self.wait(1)
        
        self.play(
            FadeOut(dasm1_arrow),
            FadeOut(dasm2_arrow),
            run_time=1
        )
       

       
        
    
    
    def animate_clock(self):
        """Animate clock hand rotation"""
        self.play(
            Rotate(
                self.clock_hand, 
                angle=-PI/6, 
                about_point=self.clock_hand.get_start(),
                rate_func=smooth
            ),
            run_time=1.5
        )