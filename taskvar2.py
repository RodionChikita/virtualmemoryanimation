from manim import *
import numpy as np

class VirtualMemoryAnimation(Scene):
    def construct(self):
        # Colors
        CODE_HIGHLIGHT = YELLOW
        MEMORY_HIGHLIGHT = GREEN
        ERROR_HIGHLIGHT = RED
        ARROW_COLOR = BLUE
        OS_COLOR = PURPLE
        CLOCK_COLOR = WHITE
        
        # Font sizes
        CODE_FONT_SIZE = 20
        MEMORY_FONT_SIZE = 18
        API_FONT_SIZE = 16
        
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
        os_rect = Rectangle(width=4, height=1.5, color=OS_COLOR, stroke_width=2)
        os_title = Text("Операционная Система", font_size=20).next_to(os_rect, UP, buff=0.2)
        
        # WinAPI functions
        api_functions = ["VirtualAlloc()", "HeapAlloc()", "VirtualFree()"]
        api_text = VGroup(*[
            Text(func, font_size=API_FONT_SIZE, font="Monospace")
            for func in api_functions
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        api_text.move_to(os_rect.get_center())
        
        # Clock
        clock_circle = Circle(radius=0.25, color=CLOCK_COLOR, stroke_width=2)
        clock_center = clock_circle.get_center()
        clock_hand = Line(clock_center, clock_center + UP * 0.15, color=CLOCK_COLOR, stroke_width=2)
        clock_text = Text("Часы", font_size=12).next_to(clock_circle, DOWN, buff=0.1)
        clock_group = VGroup(clock_circle, clock_hand, clock_text)
        clock_group.next_to(os_rect, RIGHT, buff=0.3)
        
        os_group.add(os_title, os_rect, api_text, clock_group)
        os_group.move_to(UP * 2.5)  # Top center
        
        # 3. Stack Memory (TOP RIGHT)
        stack_rect = Rectangle(width=3, height=2, color=BLUE, stroke_width=2)
        stack_title = Text("Стек", font_size=20).next_to(stack_rect, UP, buff=0.2)
        
        # Stack addresses (growing downward - high addresses)
        stack_addresses = ["0x7ffd1234", "0x7ffd1230", "0x7ffd122c", "0x7ffd1228"]
        stack_text = VGroup(*[
            Text(addr, font_size=MEMORY_FONT_SIZE, font="Monospace")
            for addr in stack_addresses
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        stack_text.move_to(stack_rect.get_center())
        
        stack_group.add(stack_title, stack_rect, stack_text)
        stack_group.move_to(RIGHT * 4 + UP * 1)  # Top right
        
        # 4. Heap Memory (BOTTOM RIGHT)
        heap_rect = Rectangle(width=3, height=2, color=GREEN, stroke_width=2)
        heap_title = Text("Динамическая память", font_size=20).next_to(heap_rect, UP, buff=0.2)
        
        # Heap addresses (different range - low addresses)
        heap_addresses = ["0x55a11000", "0x55a12000", "0x55a13000", "0x55a14000"]
        heap_size_labels = ["4096 байт", "4096 байт", "4096 байт", "4096 байт"]
        
        # Create heap blocks as separate VGroups
        self.heap_block_groups = VGroup()
        for i, (addr, size) in enumerate(zip(heap_addresses, heap_size_labels)):
            block_group = VGroup()
            addr_text = Text(addr, font_size=MEMORY_FONT_SIZE-2, font="Monospace")
            size_text = Text(size, font_size=MEMORY_FONT_SIZE-4, color=GRAY)
            block_group.add(addr_text, size_text)
            block_group.arrange(DOWN, center=False, aligned_edge=LEFT, buff=0.1)
            self.heap_block_groups.add(block_group)
        
        self.heap_block_groups.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        self.heap_block_groups.move_to(heap_rect.get_center())
        
        heap_group.add(heap_title, heap_rect, self.heap_block_groups)
        heap_group.move_to(RIGHT * 4 + DOWN * 1.5)  # Bottom right
        
        # 5. Function block (BOTTOM CENTER)
        func_rect = Rectangle(width=3, height=0.8, color=ORANGE, stroke_width=2)
        func_title = Text("Системные вызовы", font_size=18).next_to(func_rect, UP, buff=0.2)
        
        self.malloc_text = Text("malloc()", font_size=20, font="Monospace", color=GREEN)
        self.free_text = Text("free()", font_size=20, font="Monospace", color=RED)
        
        function_group.add(func_title, func_rect)
        function_group.move_to(DOWN * 3)  # Bottom center
        
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
        self.show_free_sequence()
    
    def show_malloc_sequence(self):
        """Animate memory allocation sequence"""
        # Highlight "new int" line
        new_line = self.code_block[1]  # "    int* ptr = new int;"
        highlight_rect = SurroundingRectangle(new_line, color=YELLOW, buff=0.1, stroke_width=3)
        
        self.play(Create(highlight_rect), run_time=1)
        self.wait(0.5)
        
        # Show malloc() in function block
        func_rect = self.function_group[1]
        self.malloc_text.move_to(func_rect.get_center())
        
        self.play(Write(self.malloc_text), run_time=1)
        self.wait(0.5)
        
        # Create arrows: code -> malloc -> OS
        arrow1 = Arrow(
            highlight_rect.get_right(),
            self.malloc_text.get_left(),
            color=BLUE,
            buff=0.1,
            stroke_width=3
        )
        
        arrow2 = Arrow(
            self.malloc_text.get_top(),
            self.os_group[1].get_bottom(),  # OS rectangle
            color=BLUE,
            buff=0.1,
            stroke_width=3
        )
        
        self.play(Create(arrow1), Create(arrow2), run_time=1.5)
        self.wait(0.5)
        
        # Animate clock
        self.animate_clock()
        
        # Create memory search pointer
        search_arrow = Arrow(
            self.os_group[1].get_right(),
            self.heap_block_groups[0].get_left(),
            color=BLUE,
            buff=0.1,
            stroke_width=3,
            max_tip_length_to_length_ratio=0.15
        )
        
        self.play(Create(search_arrow), run_time=1)
        self.wait(0.5)
        
        # Search through memory blocks
        blocks_to_search = [0, 1, 2]  # First three blocks
        
        for i, block_idx in enumerate(blocks_to_search):
            current_block = self.heap_block_groups[block_idx]
            block_rect = SurroundingRectangle(current_block, buff=0.1, stroke_width=2)
            
            # Move search arrow to current block
            new_arrow = Arrow(
                self.os_group[1].get_right(),
                current_block.get_left(),
                color=BLUE,
                buff=0.1,
                stroke_width=3
            )
            self.play(
                Transform(search_arrow, new_arrow),
                run_time=0.8
            )
            
            if i < 2:  # First two blocks - not enough memory (red)
                error_rect = block_rect.copy().set_color(RED)
                self.play(Create(error_rect), run_time=0.5)
                self.wait(0.3)
                self.play(FadeOut(error_rect), run_time=0.3)
            else:  # Third block - suitable (green)
                success_rect = SurroundingRectangle(
                    current_block, 
                    color=GREEN, 
                    buff=0.1, 
                    stroke_width=4
                )
                reserved_text = Text(
                    "Блок зарезервирован\nпод программу", 
                    font_size=12, 
                    color=GREEN
                )
                reserved_text.next_to(current_block, UP, buff=0.1)
                
                self.play(
                    Create(success_rect),
                    Write(reserved_text),
                    run_time=1
                )
                
                # Store references for later use
                self.allocated_block_rect = success_rect
                self.reserved_text = reserved_text
                self.allocated_block_index = block_idx
                
                # Arrow from OS to allocated block
                arrow3 = Arrow(
                    self.os_group[1].get_bottom(),
                    success_rect.get_top(),
                    color=BLUE,
                    buff=0.1,
                    stroke_width=3
                )
                
                self.play(Create(arrow3), run_time=1)
                self.wait(1)
                
                # Store arrow reference
                self.os_to_mem_arrow = arrow3
        
        # Cleanup temporary arrows
        self.play(
            FadeOut(arrow1),
            FadeOut(arrow2),
            FadeOut(search_arrow),
            run_time=1
        )
        
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
        
        # Show value being stored in memory
        value_text = Text("42", font_size=18, color=GREEN, weight=BOLD)
        allocated_block = self.heap_block_groups[self.allocated_block_index]
        
        # Position value inside the allocated block
        value_text.move_to(allocated_block.get_center())
        
        # Arrow from code to memory
        arrow = Arrow(
            assignment_line.get_right(),
            self.allocated_block_rect.get_left(),
            color=BLUE,
            buff=0.1,
            stroke_width=3
        )
        
        self.play(Create(arrow), run_time=1)
        self.play(Write(value_text), run_time=1)
        self.wait(1)
        
        # Store value reference
        self.value_text = value_text
        
        # Cleanup arrow
        self.play(FadeOut(arrow), run_time=0.5)
        self.wait(1)
    
    def show_free_sequence(self):
        """Animate memory deallocation sequence"""
        self.wait(1)
        
        # Highlight delete line
        delete_line = self.code_block[3]  # "    delete ptr;"
        delete_highlight = SurroundingRectangle(
            delete_line, 
            color=YELLOW, 
            buff=0.1, 
            stroke_width=3
        )
        
        self.play(
            Transform(self.current_highlight, delete_highlight),
            run_time=1
        )
        self.wait(0.5)
        
        # Replace malloc with free
        func_rect = self.function_group[1]
        self.free_text.move_to(func_rect.get_center())
        
        self.play(
            Transform(self.malloc_text, self.free_text),
            run_time=1
        )
        self.wait(0.5)
        
        # Create arrows: code -> free -> OS
        arrow1 = Arrow(
            delete_line.get_right(),
            self.free_text.get_left(),
            color=BLUE,
            buff=0.1,
            stroke_width=3
        )
        
        arrow2 = Arrow(
            self.free_text.get_top(),
            self.os_group[1].get_bottom(),
            color=BLUE,
            buff=0.1,
            stroke_width=3
        )
        
        self.play(Create(arrow1), Create(arrow2), run_time=1.5)
        self.wait(0.5)
        
        # Animate clock
        self.animate_clock()
        
        # Animate memory deallocation
        self.play(
            FadeOut(self.allocated_block_rect),
            FadeOut(self.reserved_text),
            FadeOut(self.value_text),
            FadeOut(self.os_to_mem_arrow),
            run_time=1.5
        )
        
        self.wait(1)
        
        # Final cleanup
        self.play(
            FadeOut(arrow1),
            FadeOut(arrow2), 
            FadeOut(self.current_highlight),
            run_time=1
        )
        
        self.wait(2)
    
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