from manim import *
import numpy as np

class VirtualMemoryAnimation(Scene):
    def construct(self):
        # Colors
        self.OS_COLOR = PURPLE
        self.CLOCK_COLOR = WHITE
        self.REGISTRY_COLOR = TEAL_E
        
        # Font sizes
        self.CODE_FONT_SIZE = 20
        self.MEMORY_FONT_SIZE = 18
        self.API_FONT_SIZE = 16
        self.REGISTRY_FONT_SIZE = 14
        self.REGISTRY_HEADER_FONT_SIZE = 12

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
        # Подпись процесса (для связи с реестром ОС)
        self.process_name = "app.exe"
        self.process_pid = "PID 1234"
        pid_label = Text(f"Процесс: {self.process_name} ({self.process_pid})", font_size=16, color=GRAY_B)
        pid_label.next_to(code_title, UP, buff=0.1)
        code_group.add(code_title, pid_label, code_block)
        self.add(code_group)   # важно — чтобы Code отрисовался!
        self.wait(0.01) 
        code_group.scale(0.85)
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
        # Реестр выделенных областей (OS VM Registry)
        registry_rect = Rectangle(width=4.2, height=1.8, color=self.REGISTRY_COLOR, stroke_width=2)
        registry_title = Text("VAD-дерево процесса (!vad)", font_size=16).next_to(registry_rect, UP, buff=0.1)
        # Внутренние параметры таблицы (Windows: WinDbg !vad — список VAD)
        self.registry_rect = registry_rect
        inner_pad_x = 0.15
        inner_pad_y = 0.18
        usable_width = registry_rect.width - inner_pad_x * 2
        usable_height = registry_rect.height - inner_pad_y * 2
        # Колонки: VAD | Level | Start | End | Commit | Type | Protect (7 столбцов), ширины под содержимое
        # Protect шире, так как значения вида EXECUTE_WRITECOPY самые длинные
        col_fracs = [0.12, 0.08, 0.16, 0.16, 0.10, 0.15, 0.23]
        self.registry_col_widths = [f * usable_width for f in col_fracs]
        inner_left_x = registry_rect.get_left()[0] + inner_pad_x
        top_inner_y = registry_rect.get_top()[1] - inner_pad_y
        # Сохраняем для последующего точного центрирования ячеек
        self.registry_inner_left_x = inner_left_x
        # Вертикальные разделители (грид)
        col_xs = [inner_left_x + sum(self.registry_col_widths[:i+1]) for i in range(len(self.registry_col_widths)-1)]
        grid_lines = VGroup(*[
            Line(np.array([x, registry_rect.get_top()[1]-inner_pad_y, 0]),
                 np.array([x, registry_rect.get_bottom()[1]+inner_pad_y, 0]),
                 stroke_width=1, color=self.REGISTRY_COLOR)
            for x in col_xs
        ])
        # Заголовки колонок (внутри прямоугольника)
        cumulative = [0]
        for w in self.registry_col_widths:
            cumulative.append(cumulative[-1] + w)
        # Сохраняем кумулятивные ширины для доступа в методах добавления строк
        self.registry_col_cumulative = cumulative
        self.registry_col_centers = [
            inner_left_x + (cumulative[i] + cumulative[i+1]) * 0.5
            for i in range(len(self.registry_col_widths))
        ]
        header_y = top_inner_y - 0.05
        h_vad = Text("VAD", font_size=self.REGISTRY_HEADER_FONT_SIZE, color=LIGHT_GRAY)
        h_lvl = Text("Level", font_size=self.REGISTRY_HEADER_FONT_SIZE, color=LIGHT_GRAY)
        h_start = Text("Start", font_size=self.REGISTRY_HEADER_FONT_SIZE, color=LIGHT_GRAY)
        h_end = Text("End", font_size=self.REGISTRY_HEADER_FONT_SIZE, color=LIGHT_GRAY)
        h_commit = Text("Commit", font_size=self.REGISTRY_HEADER_FONT_SIZE, color=LIGHT_GRAY)
        h_type = Text("Type", font_size=self.REGISTRY_HEADER_FONT_SIZE, color=LIGHT_GRAY)
        h_prot = Text("Protect", font_size=self.REGISTRY_HEADER_FONT_SIZE, color=LIGHT_GRAY)
        headers_list = [h_vad, h_lvl, h_start, h_end, h_commit, h_type, h_prot]
        for i, h in enumerate(headers_list):
            h.move_to(np.array([self.registry_col_centers[i], header_y, 0]))
            max_w = self.registry_col_widths[i] - 0.08
            if h.width > max_w:
                h.scale_to_fit_width(max_w)
        header_row = VGroup(*headers_list)
        # Нижняя линия под заголовком
        header_line = Line(
            np.array([inner_left_x, header_y - 0.12, 0]),
            np.array([inner_left_x + usable_width, header_y - 0.12, 0]),
            stroke_width=1, color=self.REGISTRY_COLOR
        )
        # Контейнер строк
        self.registry_rows = VGroup()
        self.registry_row_height = 0.26
        self.registry_first_row_y = header_y - 0.30
        # Примечание по документации — внутрь блока снизу
        docs_note = Text("WinDbg !vad: VAD, Level, Start, End, Commit, Type, Protect",
                         font_size=9, color=GRAY_B)
        docs_note.move_to(np.array([registry_rect.get_center()[0], registry_rect.get_bottom()[1] + 0.15, 0]))
        self.docs_note = docs_note
        # Собираем и размещаем ПОД блоком ОС по центру
        self.registry_group = VGroup(
            registry_title,
            registry_rect,
            grid_lines,
            header_row,
            header_line,
            self.registry_rows,
            docs_note
        )
        self.registry_group.scale(1.1)
        # Фиксируем позицию под ОС по центру сцены (чтобы не налезал)
        self.registry_group.move_to(UP * 0.2)
        os_group.add(self.registry_group)
        
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
        # Сохраняем ссылки на прямоугольник стека для вычислений границ
        self.stack_rect = stack_rect
        
        # 5. Heap Memory (BOTTOM RIGHT)
        heap_rect = Rectangle(width=4.5, height=2.75, color=GREEN, stroke_width=2)
        heap_title = Text("Динамическая память", font_size=20).next_to(heap_rect, UP, buff=0.2)
        page_info = Text("Размер страницы: 4096 байт", font_size=12, color=GRAY)
        page_info.next_to(heap_title, UP, buff=0.25)
        # Чуть опустить подписи, чтобы освободить место для волнистой линии
        heap_title.shift(DOWN * 0.15)
        page_info.shift(DOWN * 0.3)
        
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
        # Сохраняем ссылки на прямоугольник кучи для вычислений границ
        self.heap_rect = heap_rect

        # 5.1 Общая рамка вокруг стека и кучи + подпись и волнистая граница
        stack_heap_group_for_border = VGroup(stack_group, heap_group)
        memory_border = SurroundingRectangle(stack_heap_group_for_border, buff=0.35, color=GRAY_B, stroke_width=2)
        memory_border.shift(RIGHT * 0.25)
        memory_border.set_z_index(-1)
        memory_label = Text("Располагаемая память", font_size=16, color=GRAY_B).next_to(memory_border, UP, buff=0.12)
        # Волнистая линия между стеком и кучей (показывает, что это части общего пространства)
        left_x = memory_border.get_left()[0] + 0.02
        right_x = memory_border.get_right()[0] - 0.02
        mid_y = (self.stack_rect.get_bottom()[1] + self.heap_rect.get_top()[1]) / 2 + 0.12
        amp = 0.06
        freq = 5
        def wavy_func(t):
            x = left_x + (right_x - left_x) * t
            y = mid_y + amp * np.sin(2 * PI * freq * t)
            return np.array([x, y, 0])
        wavy_line = ParametricFunction(wavy_func, t_range=[0, 1], color=GRAY_B, stroke_width=2)
        # Двойная волнистая линия: копия со смещением вверх
        wavy_line2 = ParametricFunction(wavy_func, t_range=[0, 1], color=GRAY_B, stroke_width=2).shift(UP * 0.04)
        wavy_line.set_z_index(1)
        wavy_line2.set_z_index(1)
        self.memory_space_group = VGroup(memory_border, memory_label, wavy_line, wavy_line2)
        
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
                Create(self.memory_space_group),
                Create(stack_group),
                Create(heap_group),
                Create(self.dasm_group),
                lag_ratio=0.3
            ),
            run_time=3
        )
        
        self.wait(1)
        # Доп. фиксация позиции реестра ниже ОС после появления всех элементов
        self.registry_group.move_to(UP * 0.2)
        
        # Store references for animation sequences
        self.code_block = code_block
        self.function_group = function_group
        self.os_group = os_group
        self.clock_hand = clock_hand
        self.heap_group = heap_group
        self.code_group = code_group
        # Настройки завершения процесса: ExitProcess (по умолчанию) или TerminateProcess
        self.termination_mode = "ExitProcess"  # или "TerminateProcess"
        
        # Animation sequences
        self.show_malloc_sequence()
        self.show_assignment_sequence()
        self.show_crash_cleanup_sequence()
    
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

        # Значок замка рядом с адресом выделенного блока
        allocated_block_group = self.heap_lines[self.allocated_block_index]
        addr_text = allocated_block_group[1]
        lock_body = Rectangle(width=0.18, height=0.14, fill_color=YELLOW, fill_opacity=1, stroke_color=YELLOW, stroke_width=1)
        lock_shackle = Arc(radius=0.09, angle=PI, color=YELLOW, stroke_width=2)
        lock_shackle.shift(UP*0.03)
        lock_icon = VGroup(lock_shackle, lock_body).scale(1.2)
        lock_icon.next_to(addr_text, RIGHT, buff=0.22).align_to(addr_text, DOWN)
        self.lock_icon = lock_icon
        self.play(FadeIn(self.lock_icon), run_time=0.3)

        # Добавляем запись в реестр виртуальной памяти ОС
        start_addr = "0x55a13000"
        end_addr = "0x55a14000"
        # Добавляем строку VAD (!vad): уровень, старт/энд (VPN), коммит, тип, защита
        base_int = int(start_addr, 16)
        end_int = int(end_addr, 16) - 1
        start_vpn = f"{base_int // 4096:X}".lower()
        end_vpn = f"{end_int // 4096:X}".lower()
        # Псевдо-адрес узла VAD для визуализации (детерминированно от адреса)
        vad_addr = f"{(base_int ^ 0x82741BF8) & 0xFFFFFFFF:X}".lower()
        self.add_registry_entry_vad(vad_addr=vad_addr, level=2, start_vpn=start_vpn, end_vpn=end_vpn,
                                    commit_pages=1, type_text="Private", prot_text="EXECUTE_READWRITE")

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

    # --- Дополнения: Реестр ОС и освобождение при краше ---
    def add_registry_entry(self, pid_text, start_addr, end_addr, state_text="Зарезервировано"):
        """[Deprecated] Сохранено для совместимости. Делегирует Windows-версии."""
        size = self._calc_region_size(start_addr, end_addr)
        self.add_registry_entry_windows(start_addr, size, "MEM_COMMIT", "PAGE_READWRITE", "MEM_PRIVATE")

    def add_registry_entry_windows(self, base_addr: str, region_size_bytes: int,
                                   state: str, protect: str, mem_type: str):
        """Добавляет строку в реестр (Windows MEMORY_BASIC_INFORMATION)"""
        reg_rect = self.registry_rect
        reg_high = SurroundingRectangle(reg_rect, color=YELLOW, buff=0.02, stroke_width=3)
        self.play(Create(reg_high), run_time=0.4)

        # Координаты следующей строки
        row_index = len(self.registry_rows)
        row_y = self.registry_first_row_y - self.registry_row_height * row_index
        # Ячейки: База | Размер | Состояние | Защита | Тип
        base = Text(base_addr, font_size=self.REGISTRY_FONT_SIZE, font="Monospace")
        size_cell = Text(f"{region_size_bytes}", font_size=self.REGISTRY_FONT_SIZE, font="Monospace")
        state_cell = Text(state, font_size=self.REGISTRY_FONT_SIZE, font="Monospace", color=GREEN_E)
        prot_cell = Text(protect, font_size=self.REGISTRY_FONT_SIZE, font="Monospace")
        type_cell = Text(mem_type, font_size=self.REGISTRY_FONT_SIZE, font="Monospace")
        cells = [base, size_cell, state_cell, prot_cell, type_cell]
        # Подгон по ширине столбцов (чтобы не вылезали)
        for i, cell in enumerate(cells):
            max_w = self.registry_col_widths[i] - 0.08
            if cell.width > max_w:
                cell.scale_to_fit_width(max_w)
            cell.move_to(np.array([self.registry_col_centers[i], row_y, 0]))

        row = VGroup(*cells)
        self.registry_rows.add(row)
        self.play(Write(row), run_time=0.6)
        self.play(FadeOut(reg_high), run_time=0.2)

        # для удаления позже
        self.last_registry_row = row
        self.last_registry_range = (base_addr, base_addr)
        self.last_registry_state = state_cell

    def _calc_region_size(self, start_addr: str, end_addr: str) -> int:
        try:
            return int(end_addr, 16) - int(start_addr, 16)
        except Exception:
            return 4096

    def add_registry_entry_vad(self, vad_addr: str, level: int, start_vpn: str, end_vpn: str,
                               commit_pages: int, type_text: str, prot_text: str):
        """Добавляет строку в формате WinDbg !vad (7 колонок)"""
        reg_rect = self.registry_rect
        reg_high = SurroundingRectangle(reg_rect, color=YELLOW, buff=0.02, stroke_width=3)
        self.play(Create(reg_high), run_time=0.3)

        row_index = len(self.registry_rows)
        row_center_y = self.registry_first_row_y - self.registry_row_height * row_index

        vad_cell = Text(f"{vad_addr}", font_size=self.REGISTRY_FONT_SIZE, font="Monospace")
        lvl_cell = Text(f"{level}", font_size=self.REGISTRY_FONT_SIZE, font="Monospace")
        start_cell = Text(f"{start_vpn}", font_size=self.REGISTRY_FONT_SIZE, font="Monospace")
        end_cell = Text(f"{end_vpn}", font_size=self.REGISTRY_FONT_SIZE, font="Monospace")
        commit_cell = Text(f"{commit_pages}", font_size=self.REGISTRY_FONT_SIZE, font="Monospace")
        type_cell = Text(type_text, font_size=self.REGISTRY_FONT_SIZE, font="Monospace")
        prot_cell = Text(prot_text, font_size=self.REGISTRY_FONT_SIZE, font="Monospace")
        cells = [vad_cell, lvl_cell, start_cell, end_cell, commit_cell, type_cell, prot_cell]
        # Абсолютно так же, как у шапки: центрируем по заранее вычисленным центрам колонок
        for i, cell in enumerate(cells):
            max_w = self.registry_col_widths[i] - 0.08
            if cell.width > max_w:
                cell.scale_to_fit_width(max_w)
            x = self.registry_col_centers[i]
            if i == 0:
                x -= 0.12  # VAD адрес левее (усиленное смещение)
            if i == 6:
                x += 0.12  # Protect правее (усиленное смещение)
            cell.move_to(np.array([x, row_center_y, 0]))

        row = VGroup(*cells)
        self.registry_rows.add(row)
        self.play(Write(row), run_time=0.5)
        self.play(FadeOut(reg_high), run_time=0.2)

        # запоминаем последнюю добавленную строку для удаления при аварии
        self.last_registry_row = row

        # total vads — не показываем, оставляем статичную подпись

    def show_crash_cleanup_sequence(self):
        """Показать, как ОС освобождает ресурсы при аварийном завершении процесса"""
        self.wait(0.8)
        # Симулируем аварийное завершение: процесс исчезает
        crash_note_bg = Rectangle(width=4.5, height=0.5, fill_color=BLACK, fill_opacity=0.9, stroke_color=RED, stroke_width=1)
        crash_note_text = Text("Процесс аварийно завершился", font_size=16, color=RED)
        crash_note = VGroup(crash_note_bg, crash_note_text)
        crash_note.next_to(self.code_group, DOWN, buff=0.2).align_to(self.code_group, LEFT)

        self.play(Create(crash_note), run_time=0.5)

        # Очистка лишних стрелок и подсветок перед удалением процесса
        # - стрелки (Arrow)
        arrows_to_remove = [m for m in self.mobjects if isinstance(m, Arrow)]
        # - подсветки (SurroundingRectangle)
        sr_to_remove = [m for m in self.mobjects if m.__class__.__name__ == "SurroundingRectangle"]
        fade_list = []
        if hasattr(self, "current_highlight"):
            fade_list.append(self.current_highlight)
        if hasattr(self, "old_heap_high"):
            fade_list.append(self.old_heap_high)
        fade_list.extend(arrows_to_remove)
        fade_list.extend(sr_to_remove)
        if fade_list:
            self.play(*[FadeOut(m) for m in fade_list], run_time=0.4)

        # Вернуть занятое место в стеке к "0x00000000" (строка ptr)
        try:
            ptr_entry_group = self.stack_lines[1]
            old_ptr_text = ptr_entry_group[2]
            zero_text = Text("0x00000000", font_size=self.MEMORY_FONT_SIZE-2, font="Monospace", color=LIGHT_GRAY)
            zero_text.move_to(old_ptr_text.get_center())
            self.play(Transform(old_ptr_text, zero_text), run_time=0.3)
            ptr_entry_group.remove(old_ptr_text)
            ptr_entry_group.add(zero_text)
        except Exception:
            pass

        self.play(FadeOut(self.code_group), FadeOut(self.dasm_group), run_time=0.9)

        # ОС обращается к реестру (краткая индикация без стрелок и лишних подсветок)
        reg_rect = self.registry_rect
        self.play(Indicate(reg_rect, color=YELLOW), run_time=0.6)

        # Обновляем heap-блок: становится свободным (освобождение VAD/страниц)
        allocated_block_group = self.heap_lines[self.allocated_block_index]
        old_block_text = allocated_block_group[2]
        freed_text = Text("[занято 0 байт]", font_size=self.MEMORY_FONT_SIZE-2, font="Monospace", color=LIGHT_GRAY)
        freed_text.move_to(old_block_text.get_center())
        self.play(Transform(old_block_text, freed_text), run_time=0.7)
        allocated_block_group.remove(old_block_text)
        allocated_block_group.add(freed_text)

        # Убираем метки выделения
        if hasattr(self, "reserved_group"):
            self.play(FadeOut(self.reserved_group), run_time=0.3)
        if hasattr(self, "allocated_block_rect"):
            self.play(FadeOut(self.allocated_block_rect), run_time=0.3)
        if hasattr(self, "lock_icon"):
            self.play(FadeOut(self.lock_icon), run_time=0.3)

        # Удаляем запись из реестра
        if hasattr(self, "last_registry_row"):
            self.play(FadeOut(self.last_registry_row), run_time=0.4)
            try:
                self.registry_rows.remove(self.last_registry_row)
            except Exception:
                pass

        # Пошаговые действия по Windows docs (лаконичные подписи)
        steps = []
        steps.append(Text("Треды помечены на завершение", font_size=12, color=GRAY_B))
        if self.termination_mode == "ExitProcess":
            steps.append(Text("DLL: процесс детачится (ExitProcess)", font_size=12, color=GRAY_B))
        else:
            steps.append(Text("DLL: без уведомления (TerminateProcess)", font_size=12, color=GRAY_B))
        steps.append(Text("Хендлы закрыты; объекты живут, если есть другие ссылки", font_size=12, color=GRAY_B))
        # Коды выхода
        exit_code = "0xC0000005"  # фатальное исключение (пример)
        steps.append(Text(f"Exit code: {exit_code}; процесс сигнализирован", font_size=12, color=GRAY_B))
        steps_v = VGroup(*steps).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        steps_v.next_to(self.os_group, DOWN, buff=0.25).align_to(self.os_group, LEFT)
        self.play(FadeIn(steps_v), run_time=0.4)
        self.wait(0.6)
        self.play(FadeOut(steps_v), FadeOut(crash_note), run_time=0.4)