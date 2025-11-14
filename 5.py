from manim import *


class VirtualMemoryDemo(Scene):
    def construct(self):
        # ============ 1. КОД СЛЕВА ============
        code_lines = [
            "int main() {",
            "    int* p = new int;",
            "    *p = 42;",
            "    delete p;",
            "}"
        ]

        code_texts = VGroup()
        for i, line in enumerate(code_lines):
            t = Text(line, font="Consolas", font_size=32)
            if i == 0:
                t.align_to(ORIGIN, LEFT)
            else:
                t.next_to(code_texts[-1], DOWN, aligned_edge=LEFT, buff=0.18)
            code_texts.add(t)

        code_rect = SurroundingRectangle(code_texts, buff=0.3, color=WHITE, stroke_width=2)
        code_title = Text("Код программы", font_size=30)
        code_title.next_to(code_rect, UP, buff=0.25)

        code_block = VGroup(code_rect, code_texts, code_title)
        code_block.scale(0.85)
        code_block.move_to(LEFT * 5 + DOWN * 0.3)

        self.play(FadeIn(code_block))
        self.wait(0.2)

        highlight = SurroundingRectangle(code_texts[1], buff=0.05, color=YELLOW, stroke_width=3)
        self.play(Create(highlight))
        self.wait(0.2)

        # ============ 2. ОС + ФУНКЦИИ В ЦЕНТРЕ СВЕРХУ ============
        os_rect = RoundedRectangle(width=4.0, height=1.5, corner_radius=0.15,
                                   color=BLUE, stroke_width=2)
        os_title = Text("ОС", font_size=32, weight=BOLD)
        winapi_text = Text("WinAPI", font_size=24)

        os_title.move_to(os_rect.get_top() + DOWN * 0.35)
        winapi_text.next_to(os_title, DOWN, buff=0.15)

        clock_circle = Circle(radius=0.22, stroke_width=2)
        clock_circle.next_to(os_rect, RIGHT, buff=0.4)
        clock_center = clock_circle.get_center()
        clock_hand1 = Line(clock_center, clock_center + UP * 0.14, stroke_width=2)
        clock_hand2 = Line(clock_center, clock_center + RIGHT * 0.11, stroke_width=2)

        os_block = VGroup(os_rect, os_title, winapi_text,
                          clock_circle, clock_hand1, clock_hand2)

        func_rect = RoundedRectangle(width=4.0, height=1.5, corner_radius=0.15,
                                     color=PURPLE, stroke_width=2)
        func_title = Text("Функции управления памятью", font_size=22)
        func_title.scale(0.9)
        malloc_text = Text("malloc()", font_size=24, color=GREEN)
        free_text = Text("free()", font_size=24, color=RED)

        func_title.move_to(func_rect.get_top() + DOWN * 0.35)
        malloc_text.next_to(func_title, DOWN, buff=0.12)
        free_text.next_to(malloc_text, DOWN, buff=0.12)

        func_block = VGroup(func_rect, func_title, malloc_text, free_text)

        center_group = VGroup(os_block, func_block)
        center_group.arrange(DOWN, buff=0.4)
        center_group.scale(0.8)
        center_group.move_to(UP * 2.6)

        self.play(FadeIn(os_block))
        self.play(FadeIn(func_block))
        self.wait(0.2)

        # ============ 3. СТЕК + КУЧА СПРАВА ============

        # ----- Стек -----
        stack_rect = RoundedRectangle(width=3.5, height=1.7, corner_radius=0.12,
                                      color=TEAL, stroke_width=2)
        stack_title = Text("Стек", font_size=24)
        stack_title.move_to(stack_rect.get_top() + DOWN * 0.3)

        stack_addrs = [
            "0x7FFFEFFC",
            "0x7FFFEFF8",
            "0x7FFFEFF4",
            "0x7FFFEFF0",
        ]
        stack_addr_texts = VGroup()
        for i, addr in enumerate(stack_addrs):
            t = Text(addr, font_size=18)
            if i == 0:
                t.move_to(stack_rect.get_top() + DOWN * 0.75 + LEFT * 0.6)
            else:
                t.next_to(stack_addr_texts[-1], DOWN, aligned_edge=LEFT, buff=0.06)
            stack_addr_texts.add(t)

        stack_block = VGroup(stack_rect, stack_title, stack_addr_texts)

        # ----- Куча -----
        num_heap_segments = 3
        heap_segments = VGroup()
        for _ in range(num_heap_segments):
            seg = Rectangle(width=3.1, height=0.42,
                            stroke_color=WHITE, stroke_width=2)
            heap_segments.add(seg)
        heap_segments.arrange(DOWN, buff=0.12)

        heap_base_addr = 0x00400000
        page_size = 0x00001000
        heap_addr_labels = VGroup()
        for i, seg in enumerate(heap_segments):
            addr_value = heap_base_addr + i * page_size
            addr_str = f"0x{addr_value:08X}"
            addr_text = Text(addr_str, font_size=16)
            addr_text.next_to(seg, LEFT, buff=0.12)
            heap_addr_labels.add(addr_text)

        heap_content = VGroup(heap_segments, heap_addr_labels)
        heap_content.arrange(RIGHT, buff=0.0)
        heap_content.move_to(ORIGIN)

        heap_rect = RoundedRectangle(
            corner_radius=0.12,
            color=ORANGE,
            stroke_width=2
        )
        heap_rect.surround(heap_content, buff=0.25)

        heap_title = Text("Динамическая память (куча / виртуальная память)", font_size=18)
        heap_title.scale(0.9)
        heap_title.next_to(heap_rect, UP, buff=0.12)

        heap_block = VGroup(heap_rect, heap_content, heap_title)

        memory_group = VGroup(stack_block, heap_block)
        memory_group.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        memory_group.scale(0.8)
        memory_group.move_to(RIGHT * 4.8 + DOWN * 0.3)

        stack_rect = stack_block[0]
        heap_rect = heap_block[0]
        heap_content = heap_block[1]
        heap_segments = heap_content[0]
        heap_addr_labels = heap_content[1]
        heap_title = heap_block[2]

        self.play(FadeIn(stack_block))
        self.play(FadeIn(heap_block))
        self.wait(0.3)

        # ============ 4. СЦЕНА 1: new -> malloc -> ОС -> поиск блока ============
        self.play(highlight.animate.move_to(code_texts[1]))
        self.wait(0.2)

        arrow_code_to_func = Arrow(
            code_texts[1].get_right(),
            func_rect.get_left(),
            buff=0.25,
            stroke_width=3
        )
        self.play(Create(arrow_code_to_func))
        self.wait(0.2)

        self.play(Indicate(malloc_text, color=GREEN))
        self.wait(0.2)

        arrow_func_to_os = Arrow(
            func_rect.get_top(),
            os_rect.get_bottom(),
            buff=0.12,
            stroke_width=3
        )
        self.play(Create(arrow_func_to_os))
        self.play(Indicate(os_block, color=BLUE))
        self.wait(0.2)

        pointer = Triangle(fill_color=YELLOW, fill_opacity=1,
                           stroke_color=BLACK, stroke_width=1.5)
        pointer.scale(0.15)
        pointer.rotate(-PI / 2)
        pointer.next_to(heap_segments[0], LEFT, buff=0.2)

        self.play(FadeIn(pointer))
        self.wait(0.15)

        not_enough_label = Text("Мало памяти", font_size=16, color=RED)
        not_enough_label.next_to(heap_segments[0], UP, buff=0.08)

        self.play(pointer.animate.move_to(heap_segments[0].get_left() + RIGHT * 0.3))
        self.play(
            heap_segments[0].animate.set_fill(RED, opacity=0.25),
            heap_segments[0].animate.set_stroke(RED, width=3),
            FadeIn(not_enough_label)
        )
        self.wait(0.4)

        self.play(
            heap_segments[0].animate.set_fill(BLACK, opacity=0.0),
            heap_segments[0].animate.set_stroke(WHITE, width=2),
            FadeOut(not_enough_label)
        )

        reserved_label = Text("Блок зарезервирован под программу", font_size=16, color=GREEN)
        reserved_label.next_to(heap_title, UP, buff=0.08)

        # >>> СДВИГАЕМ page_label ПРАВО ОТ БЕЛОГО АДРЕСА <<<
        page_label = Text("page = 4096 байт", font_size=14, color=GREEN)
        page_label.next_to(heap_addr_labels[1], RIGHT, buff=0.2)

        self.play(pointer.animate.move_to(heap_segments[1].get_left() + RIGHT * 0.3))
        self.play(
            heap_segments[1].animate.set_fill(GREEN, opacity=0.3),
            heap_segments[1].animate.set_stroke(GREEN, width=3),
            FadeIn(page_label),
            FadeIn(reserved_label)
        )
        self.wait(0.6)

        self.play(
            FadeOut(arrow_func_to_os),
            FadeOut(arrow_code_to_func),
        )
        self.wait(0.2)

        # ============ 5. СЦЕНА 2: *p = 42 ============
        self.play(highlight.animate.move_to(code_texts[2]))
        self.wait(0.2)

        arrow_code_to_heap_write = Arrow(
            code_rect.get_right(),
            heap_rect.get_left() + DOWN * 0.5,
            buff=0.3,
            stroke_width=3
        )

        self.play(Create(arrow_code_to_heap_write))
        self.wait(0.2)

        value_text = Text("42", font_size=26, color=WHITE)
        value_text.move_to(heap_segments[1].get_center())

        self.play(FadeIn(value_text, scale=1.2))
        self.wait(0.5)

        self.play(FadeOut(arrow_code_to_heap_write))
        self.wait(0.2)

        # ============ 6. СЦЕНА 3: delete p -> free() ============
        self.play(highlight.animate.move_to(code_texts[3]))
        self.wait(0.2)

        arrow_code_to_func_free = Arrow(
            code_texts[3].get_right(),
            func_rect.get_left(),
            buff=0.28,
            stroke_width=3
        )
        arrow_func_to_heap_free = Arrow(
            func_rect.get_right() + RIGHT * 0.1,
            heap_rect.get_left() + DOWN * 0.4,
            buff=0.25,
            stroke_width=3
        )

        self.play(Create(arrow_code_to_func_free))
        self.play(Indicate(free_text, color=RED))
        self.play(Create(arrow_func_to_heap_free))
        self.wait(0.3)

        freed_label = Text("Память освобождена", font_size=16, color=YELLOW)
        freed_label.next_to(heap_segments[1], DOWN, buff=0.12)

        self.play(
            FadeOut(value_text),
            heap_segments[1].animate.set_fill(BLACK, opacity=0.0),
            heap_segments[1].animate.set_stroke(WHITE, width=2),
            FadeOut(page_label),
            FadeOut(reserved_label),
            FadeIn(freed_label)
        )
        self.wait(0.6)

        self.play(
            FadeOut(arrow_code_to_func_free),
            FadeOut(arrow_func_to_heap_free),
            FadeOut(pointer),
        )
        self.wait(0.4)


if __name__ == "__main__":
    from manim import tempconfig

    with tempconfig({"quality": "low_quality", "preview": True}):
        scene = VirtualMemoryDemo()
        scene.render()
