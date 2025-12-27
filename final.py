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

        self.ARROW_WIDTH = 2.2      # толщина линии
        self.ARROW_TIP_LENGTH = 0.18
        self.ARROW_TIP_WIDTH = 0.18
        
        # Create main groups with proper positioning
        code_group = VGroup()
        self.dasm_group = VGroup()
        os_group = VGroup()
        stack_group = VGroup()
        heap_group = VGroup()
        function_group = VGroup()
        
        # 1. Code block (LEFT side - centered vertically) - СИНТАКСИЧЕСКАЯ ПОДСВЕТКА
        code_string = '''int main() {
    int* ptr = new int;
    *ptr = 42;
    delete ptr;
}'''

        code_block = Code(
            code_string=code_string,
            language="cpp",
            tab_width=4,
            background="rectangle",
            add_line_numbers=False,
            formatter_style="monokai"
        )
        
        code_title = Text("Код программы", font_size=22).next_to(code_block, UP, buff=0.2)
        code_group.add(code_title, code_block)
        self.add(code_group)   # важно — чтобы Code отрисовался!
        self.wait(0.01) 
        #code_group.scale(0.7)   # или 0.
        code_group.to_edge(LEFT, buff=0.3)


        # 2. Disassembled code - СИНТАКСИЧЕСКАЯ ПОДСВЕТКА
        dasm_string = '''mov rax, [rsp + addr_ptr]
mov [rax], 42'''

        dasm_block = Code(
            code_string=dasm_string,
            language="asm",
            background="rectangle",
            add_line_numbers=False,
            formatter_style="vim"
        )
        
        dasm_title = Text("Дизассемблированный код", font_size=18).next_to(dasm_block, UP, buff=0.2)
        self.dasm_group.add(dasm_title, dasm_block)
        self.dasm_group.move_to(LEFT*3 + DOWN*2.8)
               
        # 3. OS Block (TOP CENTER)
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
        
        # 4. Stack Memory (TOP RIGHT)
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
            block_bg = Rectangle(
                width=2.4, height=0.4, 
                stroke_color=BLUE,
                stroke_width=1
            ).move_to(stack_rect.get_center() + RIGHT*0.1)
            addr_text = Text(addr, font_size=self.MEMORY_FONT_SIZE-1, font="Monospace")
            data_text = Text(data, font_size=self.MEMORY_FONT_SIZE-2, font="Monospace", color=LIGHT_GRAY)
            addr_text.move_to(stack_rect.get_left())
            data_text.move_to(block_bg.get_center())
            
            line_group = VGroup(block_bg, addr_text, data_text)
            self.stack_lines.add(line_group)
        self.stack_lines.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        self.stack_lines.move_to(stack_rect.get_center())
        
        stack_group.add(stack_title, stack_rect, self.stack_lines)
        stack_group.move_to(RIGHT * 4.7 + UP * 1.8)
        
        # 5. Heap Memory (BOTTOM RIGHT)
        heap_rect = Rectangle(width=4.5, height=2.75, color=GREEN, stroke_width=2)
        heap_title = Text("Динамическая память", font_size=20).next_to(heap_rect, UP, buff=0.2)
        page_info = Text("Размер страницы: 4096 байт", font_size=12, color=GRAY)
        page_info.next_to(heap_title, UP, buff=0.1)
        
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
        heap_group.move_to(RIGHT * 4.7 + DOWN * 1.8)
        
        # 6. Function block (CENTER)
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
                Create(self.dasm_group),
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
    
    def show_malloc_sequence(self):
        API_HIGHLIGHT = YELLOW

        # Получаем строки кода (универсальный способ — работает в любой версии manim)
        
        # Берём вторую строку (int* ptr = new int;)
        highlight_rect = self.highlight_code_line(self.code_block, 1)
        self.play(Create(highlight_rect))
        self.current_highlight = highlight_rect

        func_rect = self.function_group[1]
        self.malloc_text.move_to(func_rect.get_center())

        self.play(
            Create(self.function_group),
            Write(self.malloc_text),
            run_time=1
        )

        self.wait(0.5)

        arrow_start = highlight_rect.get_top() + RIGHT*1.5
        arrow_end = func_rect.get_bottom() + RIGHT*0.3
        func_arrow = self.make_arrow(arrow_start, arrow_end)

        self.play(Create(func_arrow))
        self.wait(0.5)

        # -------- Подсветка VirtualAlloc --------
        heapalloc_highlight = SurroundingRectangle(
            self.api_texts[0], 
            color=API_HIGHLIGHT, 
            buff=0.1, 
            stroke_width=3
        )
        self.old_heap_high = heapalloc_highlight

        arrow_start = func_rect.get_right()
        arrow_end = heapalloc_highlight.get_left()
        func1_arrow = self.make_arrow(arrow_start, arrow_end)
        
        self.play(Create(func1_arrow), run_time=1)
        self.wait(0.5)
        
        self.play(Create(heapalloc_highlight), run_time=1)
        self.wait(0.5)

        # -------- Поиск подходящего блока --------
        pointer_triangle = Triangle(color=YELLOW, fill_opacity=1, stroke_width=2).scale(0.08)
        pointer_triangle.rotate(-90 * DEGREES)
        first_heap_block = self.heap_lines[0]
        pointer_triangle.move_to(first_heap_block.get_left() + LEFT * 0.2)

        self.play(Create(pointer_triangle))
        self.wait(0.5)

        blocks_to_search = [0, 1, 2]

        self.play(FadeOut(func_arrow), FadeOut(func1_arrow))

        for i, block_idx in enumerate(blocks_to_search):
            current_block = self.heap_lines[block_idx]

            pointer_target = current_block.get_left() + LEFT * 0.2
            self.play(pointer_triangle.animate.move_to(pointer_target), run_time=0.8)

            self.animate_clock()

            if i < 2:
                error_rect = SurroundingRectangle(current_block, buff=0.05).set_color(RED)

                reason_bg = Rectangle(
                    width=2.5, height=0.4, fill_color=BLACK,
                    fill_opacity=1, stroke_color=RED, stroke_width=1
                )
                reason_text = Text("Мало свободного места!", font_size=12, color=RED)
                reason_group = VGroup(reason_bg, reason_text)
                reason_group.next_to(current_block, UP, buff=0.1)

                self.play(Create(error_rect), Create(reason_group), run_time=0.8)
                self.wait(0.5)
                self.play(FadeOut(error_rect), FadeOut(reason_group), run_time=0.3)

            else:
                # Успех
                success_rect = SurroundingRectangle(
                    current_block, color=GREEN, buff=0.05, stroke_width=4
                )

                reserved_bg = Rectangle(
                    width=2.2, height=0.4, fill_color=BLACK,
                    fill_opacity=0.9, stroke_color=GREEN, stroke_width=1
                )
                reserved_text = Text("Блок зарезервирован", font_size=11, color=GREEN)
                reserved_group = VGroup(reserved_bg, reserved_text)
                reserved_group.next_to(current_block, UP, buff=0.1)

                self.play(Create(success_rect), Create(reserved_group), run_time=1)

                self.allocated_block_rect = success_rect
                self.reserved_group = reserved_group
                self.allocated_block_index = block_idx
                self.wait(1)

        # --- Вылетающий адрес ----
        allocated_block = self.heap_lines[self.allocated_block_index]
        addr_text = allocated_block[1]   # текст адреса (левый столбец)

        # копия адреса для анимации
        flying_addr = addr_text.copy().set_color(YELLOW)
        flying_addr.move_to(addr_text.get_center())

        self.play(
            flying_addr.animate.set_opacity(1),
            Flash(addr_text, color=YELLOW, line_length=0.2),
            run_time=0.6
        )

        # путь от адреса до ОС
        arrow_path_start = addr_text.get_center()
        arrow_path_end = self.old_heap_high.get_bottom() + RIGHT*0.3

        arrow_path = Line(arrow_path_start, arrow_path_end)

        # стрелка под летящим адресом
        arrow_back = self.make_arrow(arrow_path_start, arrow_path_end)

        self.play(Create(arrow_back), run_time=0.6)

        # движение "вылетевшего" адреса по пути
        self.play(
            MoveAlongPath(flying_addr, arrow_path),
            run_time=1.4
        )

        # исчезновение адреса, запись в стек произойдёт позже
        self.play(FadeOut(flying_addr))
        self.wait(0.3)


        # -------- Возврат стрелок --------
       

        arrow_end = func_rect.get_right()
        arrow_start = heapalloc_highlight.get_left()
        func_back_arrow = self.make_arrow(arrow_start, arrow_end)
        self.play(Create(func_back_arrow))
        self.wait(0.5)

        arrow_end =  highlight_rect.get_top() + RIGHT*1.5
        arrow_start = func_rect.get_bottom() + RIGHT*0.3
        func_back1_arrow = self.make_arrow(arrow_start, arrow_end)
        self.play(Create(func_back1_arrow))
        self.wait(0.5)

        self.update_stack_with_pointer("0x55a13000")

        self.play(
            FadeOut(func_back_arrow),
            FadeOut(func_back1_arrow),
            FadeOut(arrow_back),
            FadeOut(self.function_group),
            FadeOut(self.malloc_text),
        )

        self.wait(0.5)

    def update_stack_with_pointer(self, pointer_address):
        """Update stack with the allocated pointer"""
        stack_entry = self.stack_lines[1]
        old_data_text = stack_entry[2]
        
        new_data_text = Text(f"ptr={pointer_address}", 
                            font_size=self.MEMORY_FONT_SIZE-2, 
                            font="Monospace", 
                            color=YELLOW)
        new_data_text.move_to(old_data_text.get_center())
        
        self.play(
            Transform(old_data_text, new_data_text),
            run_time=1
        )
        
        stack_entry.remove(old_data_text)
        stack_entry.add(new_data_text)

    def show_assignment_sequence(self):
        """Animate variable assignment sequence"""
        self.wait(1)

        # Получаем строки
        new_highlight = self.highlight_code_line(self.code_block, 2)
        

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
        
        arrow_start = new_highlight.get_bottom() + RIGHT*0.4
        arrow_end = self.dasm_group.get_top()
        dasm1_arrow = Arrow(arrow_start, arrow_end, color=YELLOW, buff=0.1, stroke_width=2)
        
        self.play(Create(dasm1_arrow), run_time=1)
        self.wait(0.5)



        # Записываем значение в выделенный блок
        allocated_block_group = self.heap_lines[self.allocated_block_index]
        old_data_text = allocated_block_group[2]

        arrow_start = self.dasm_group.get_right()
        arrow_end = allocated_block_group.get_left()
        dasm2_arrow = Arrow(arrow_start, arrow_end, color=YELLOW, buff=0.1, stroke_width=2)
        
        self.play(Create(dasm2_arrow), run_time=1)
        self.wait(0.5)

        new_data_text = Text("42", font_size=self.MEMORY_FONT_SIZE-2,
                            font="Monospace", color=YELLOW)
        new_data_text.move_to(old_data_text.get_center())

        self.play(Transform(old_data_text, new_data_text), run_time=1)

        allocated_block_group.remove(old_data_text)
        allocated_block_group.add(new_data_text)

        self.wait(1)

    def highlight_code_line(self, code_block, line_index, color=YELLOW):
        # Достаём строку
        lines_group = code_block.submobjects[1]
        line = lines_group[line_index]

        # Берём только реальные фрагменты текста (цветные элементы)
        chunks = [m for m in line.submobjects if m.get_width() > 0.001]

        xs = [c.get_x() for c in chunks]
        ys = [c.get_y() for c in chunks]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        width = max_x - min_x
        height = max_y - min_y

        # Рамка, чуть увеличенная
        rect = Rectangle(
            width=width + 0.15,
            height=height + 0.3,
            stroke_color=color,
            stroke_width=3
        )

        rect.move_to([(min_x + max_x)/2, (min_y + max_y)/2 - 0.02, 0])
        return rect



    def make_arrow(self, start, end, color=YELLOW):
        return Arrow(
            start,
            end,
            color=color,
            buff=0.1,
            stroke_width=self.ARROW_WIDTH,
            max_tip_length_to_length_ratio=0.25,   # фиксированный размер наконечника
            max_stroke_width_to_length_ratio=1     # делает наконечник стабильным
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