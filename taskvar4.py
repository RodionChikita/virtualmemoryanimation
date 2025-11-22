from manim import *
import numpy as np

class VirtualMemoryAnimation(Scene):
    def construct(self):
        # Colors
        OS_COLOR = PURPLE
        CLOCK_COLOR = WHITE
        
        # Font sizes
        CODE_FONT_SIZE = 20
        MEMORY_FONT_SIZE = 18
        self.API_FONT_SIZE = 16
        
        # Create main groups with proper positioning
        code_group = VGroup()
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
        
        code_block = VGroup(*[
            Text(line, font_size=CODE_FONT_SIZE, font="Monospace") 
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
        
        # 2. OS Block (TOP CENTER)
        os_rect = Rectangle(width=3.5, height=1.5, color=OS_COLOR, stroke_width=2)
        os_title = Text("Операционная Система", font_size=20).next_to(os_rect, UP, buff=0.2)
        
        # WinAPI functions
        api_functions = ["VirtualAlloc()", "HeapAlloc()", "VirtualFree()"]
        self.api_texts = VGroup(*[
            Text(func, font_size=self.API_FONT_SIZE, font="Monospace")
            for func in api_functions
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        self.api_texts.move_to(os_rect.get_left() + RIGHT*1.3)
        
        # Clock INSIDE OS rectangle
        clock_circle = Circle(radius=0.2, color=CLOCK_COLOR, stroke_width=2)
        clock_center = clock_circle.get_center()
        clock_hand = Line(clock_center, clock_center + UP * 0.12, color=CLOCK_COLOR, stroke_width=2)
        clock_group = VGroup(clock_circle, clock_hand)
        clock_group.move_to(os_rect.get_right() + LEFT*0.5)
        
        os_group.add(os_title, os_rect, self.api_texts, clock_group)
        os_group.move_to(UP * 2.5)  # Top center
        
        # 3. Stack Memory (TOP RIGHT) READY!!!
        stack_rect = Rectangle(width=4.5, height=2.75, color=BLUE, stroke_width=2)
        stack_title = Text("Стек", font_size=20).next_to(stack_rect, UP, buff=0.2)

        stack_data = [
            ("0x7ffd1234", "main()"),
            ("0x7ffd1230", "ptr=0x55a13000"),
            ("0x7ffd122c", "0x00000000"),
            ("0x7ffd1228", "0xdddddddd"),
            ("0x7ffd1224", "0xffffffff")
        ]

        stack_lines = VGroup()
        for addr, data in stack_data:
            # Create background block for each stack entry
            block_bg = Rectangle(
                width=2.4, height=0.4, 
                stroke_color=BLUE,
                stroke_width=1
            ).move_to(stack_rect.get_center() + RIGHT*0.1)
            addr_text = Text(addr, font_size=MEMORY_FONT_SIZE-1, font="Monospace")
            data_text = Text(data, font_size=MEMORY_FONT_SIZE-2, font="Monospace", color=LIGHT_GRAY)
            addr_text.move_to(stack_rect.get_left())
            data_text.move_to(block_bg.get_center())  # Moved more right
            
            line_group = VGroup(block_bg, addr_text, data_text)
            stack_lines.add(line_group)
        stack_lines.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        stack_lines.move_to(stack_rect.get_center())
        
        stack_group.add(stack_title, stack_rect, stack_lines)
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

        self.heap_lines = VGroup()
        for addr,data in heap_data:
            block_hp = Rectangle(
                width=2.7, height=0.4, 
                stroke_color=BLUE,
                stroke_width=1
            ).move_to(heap_rect.get_center() + RIGHT*0.1)
            hp_addr_text = Text(addr, font_size=MEMORY_FONT_SIZE-1, font="Monospace")
            hp_data_text = Text(data, font_size=MEMORY_FONT_SIZE-2, font="Monospace", color=LIGHT_GRAY)
            hp_addr_text.move_to(heap_rect.get_left())
            hp_data_text.move_to(block_hp.get_center())

            hp_line_group = VGroup(block_hp, hp_addr_text, hp_data_text)
            self.heap_lines.add(hp_line_group)
        self.heap_lines.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        self.heap_lines.move_to(heap_rect.get_center())
        
        heap_group.add(heap_title, heap_rect, self.heap_lines, page_info)
        heap_group.move_to(RIGHT * 4.7 + DOWN * 1.8)  # Bottom right
        
        # 5. Function block (CENTER - между кодом и памятью)
        func_rect = Rectangle(width=3, height=0.8, color=ORANGE, stroke_width=2)
        func_title = Text("Системные вызовы", font_size=18).next_to(func_rect, UP, buff=0.2)
        
        self.malloc_text = Text("malloc()", font_size=20, font="Monospace", color=GREEN)
        self.free_text = Text("free()", font_size=20, font="Monospace", color=RED)
        
        function_group.add(func_title, func_rect)
          # Center position
        
        # Create all static elements with proper positioning
        self.play(
            LaggedStart(
                Create(code_group),
                Create(os_group),
                Create(stack_group),
                Create(heap_group),
                Create(function_group),
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
        API_HIGHLIGHT = YELLOW
        # Highlight "new int" line
        new_line = self.code_block[1]  # "    int* ptr = new int;"
        highlight_rect = SurroundingRectangle(new_line, color=YELLOW, buff=0.1, stroke_width=3)
        
        self.play(Create(highlight_rect), run_time=1)
        self.wait(0.5)
        
        # Show malloc() in function block (CENTER)
        func_rect = self.function_group[1]
        self.malloc_text.move_to(func_rect.get_center())
        
        self.play(Write(self.malloc_text), run_time=1)
        self.wait(0.5)
        
        # Highlight HeapAlloc() API function
        heapalloc_highlight = SurroundingRectangle(
            self.api_texts[1], 
            color=API_HIGHLIGHT, 
            buff=0.1, 
            stroke_width=3
        )
        
        self.play(Create(heapalloc_highlight), run_time=1)
        self.wait(0.5)

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
        
        # Animate clock
        self.animate_clock()
        
        
        
        # Keep the highlight
        self.current_highlight = highlight_rect
    
    def show_assignment_sequence(self):
        """Animate variable assignment sequence"""
        self.wait(1)
        
        # Highlight assignment line
        assignment_line = self.code_block[2]  # "    *ptr = 42;"
        new_highlight = SurroundingRectangle(
            assignment_line, 
            color=YELLOW, 
            buff=0.1, 
            stroke_width=3
        )
        
        self.play(
            Transform(self.current_highlight, new_highlight),
            run_time=1
        )
        self.wait(0.5)

        heap_alloc_text = Text("HeapAlloc()", font_size=self.API_FONT_SIZE, font="Monospace", color=WHITE)
        heap_alloc_text.move_to(self.os_group[1].get_center())
        
        self.play(Write(heap_alloc_text), run_time=1)
        self.wait(0.5)

       
        
    
    
    def animate_clock(self):
        """Animate clock hand rotation"""
        self.play(
            Rotate(
                self.clock_hand, 
                angle=-2*PI/3, 
                about_point=self.clock_hand.get_start(),
                rate_func=smooth
            ),
            run_time=1.5
        )