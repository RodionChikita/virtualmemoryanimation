from manim import *

########################################
# ХЕЛПЕРЫ (обновлённые)
########################################

def make_code_block(code_text, title_text="Код", title_color=YELLOW):
    """
    Блок с заголовком и исходником.
    """
    title = Text(title_text, font_size=24, color=title_color)

    code_block = Code(
        code_string=code_text,
        language="cpp",
        formatter_style="monokai",
        add_line_numbers=False,
        background="rectangle",
        background_config={
            "stroke_color": title_color,
            "stroke_width": 2,
            "fill_opacity": 0.1,
        },
        paragraph_config={
            "font": "Consolas",
            "font_size": 20,
        },
    ).scale(0.7)

    group = VGroup(title, code_block).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
    return group


def memory_cell(value_text="5", addr_text="0x1000", color_frame=GREEN):
    """
    Одна "ячейка кучи": прямоугольник, внутри значение,
    снизу подпись адреса.
    """
    box = Rectangle(
        width=2.0,
        height=1.0,
        color=color_frame,
        stroke_width=2
    )
    val = Text(value_text, font_size=28, color=WHITE).move_to(box.get_center())
    addr = Text(addr_text, font_size=16, color=GRAY).next_to(box, DOWN, buff=0.12)
    return VGroup(box, val, addr)


def heap_container(inner=None, title="Куча (heap)", color_frame=GREEN):
    """
    Рисуем рамку "Куча (heap)".
    - Если inner == None: рисуем пустую кучу стандартного размера (без surround()).
    - Если inner есть: подгоняем рамку под содержимое.
    Возвращает VGroup(heap_label, heap_box, inner_group).
    """

    # Случай 1: кучи ещё как бы нет (до new) -> рисуем пустую коробку фиксированного размера
    if inner is None:
        inner_group = VGroup()  # пусто внутри
        # просто рисуем коробку фиксированного размера
        heap_box = Rectangle(
            width=3.0,
            height=1.8,
            color=color_frame,
            stroke_width=2,
        )
        heap_label = Text(
            title,
            font_size=20,
            color=color_frame
        ).next_to(heap_box, UP, buff=0.15)

        return VGroup(heap_label, heap_box, inner_group)

    # Случай 2: внутри есть одна или несколько ячеек памяти
    if isinstance(inner, list):
        inner_group = VGroup(*inner).arrange(DOWN, buff=0.2)
    else:
        inner_group = inner

    # строим коробку и подгоняем под содержимое
    heap_box = Rectangle(
        width=3.0,
        height=max(1.8, inner_group.height + 0.8),
        color=color_frame,
        stroke_width=2,
    )
    heap_box.move_to(inner_group.get_center())

    heap_label = Text(
        title,
        font_size=20,
        color=color_frame
    ).next_to(heap_box, UP, buff=0.15)

    return VGroup(heap_label, heap_box, inner_group)



def step_caption(text):
    """
    Подпись-шаг внизу экрана.
    Короткий текст, чтобы не уходил за границы.
    """
    return Text(text, font_size=22, color=WHITE)


def title_top(scene, text, color=BLUE):
    """
    Заголовок сцены.
    """
    t = Text(text, font_size=32, color=color)
    t.to_edge(UP)
    scene.play(Write(t), run_time=1.5)
    scene.wait(0.5)
    return t

def pointer_arrow_stack_to_heap(p_box, heap_cell, color_frame=ORANGE):
    """
    Стрелка от переменной p в стеке к ячейке в куче.
    Возвращает (стрелка + подпись "p -> heap"), при этом подпись идёт не поверх стека.
    """
    arrow = Arrow(
        p_box.get_right(),
        heap_cell.get_left(),
        buff=0.3,  # чутка больше расстояние
        color=color_frame,
        stroke_width=4,
        max_tip_length_to_length_ratio=0.15,
    )

    label = Text(
        "указатель p",
        font_size=14,  # меньше, чтобы не лезло на рамки
        color=color_frame
    ).next_to(arrow, UP, buff=0.1)

    return VGroup(arrow, label)
def stack_frame(p_addr_text="0x1000"):
    """
    Стек функции main().
    В стеке лежит переменная p, и ВНУТРИ этой переменной реально написано p = 0x1000.
    Под ней подпись-объяснение.
    """
    # рамка всего стека
    frame_box = Rectangle(
        width=3.0,
        height=1.8,
        color=RED,
        stroke_width=2,
    )

    frame_label = Text(
        "Стек функции main()",
        font_size=20,
        color=RED
    ).next_to(frame_box, UP, buff=0.15)

    # p_box — ячейка переменной p в стеке
    p_box = Rectangle(
        width=2.4,
        height=0.7,
        color=RED,
        stroke_width=2,
    )

    # содержимое ячейки p: "p = 0x1000"
    p_name = Text("p =", font_size=20, color=WHITE)
    p_val = Text(p_addr_text, font_size=20, color=YELLOW)
    p_line = VGroup(p_name, p_val).arrange(RIGHT, buff=0.1)
    p_line.move_to(p_box.get_center())

    # подпись под p_box
    p_comment = Text(
        "p — указатель на кучу",
        font_size=16,
        color=YELLOW
    ).next_to(p_box, DOWN, buff=0.2)

    # собрать внутренности стека
    stack_inner = VGroup(p_box, p_line, p_comment)
    stack_inner.move_to(frame_box.get_center())

    # итоговая группа стека
    stack_group = VGroup(frame_label, frame_box, stack_inner)

    return stack_group, p_box, p_val


class Scene1_NewDelete(Scene):
    def construct(self):
        # === Заголовок ===
        title = title_top(self, "Динамическая память: new / delete")

        # === Код программы ===
        code_text = (
            "int* p = new int(5);\n"
            "cout << *p;\n"
            "delete p;"
        )
        code_group = make_code_block(code_text, "Наш код C++", YELLOW)
        code_group.move_to(UP * 1.5)

        # === Память процесса ===
        # Куча (пока без блока)
        heap_group_obj = heap_container(None, "Куча (heap)", GREEN)

        # Стек с p
        stack_group_obj, p_box, p_val_text = stack_frame("0x1000")

        # Будущая выделенная ячейка в куче (значение 5 @ 0x1000)
        heap_cell = memory_cell("5", "0x1000", GREEN)
        heap_cell.set_opacity(0)

        # Расположение на экране:
        # стек слева, куча справа, код сверху
        stack_group_obj.move_to(LEFT * 3.5 + DOWN * 0.5)
        heap_group_obj.move_to(RIGHT * 3.5 + DOWN * 0.5)

        # Положить блок '5' ВНУТРИ кучи, строго по центру рамки кучи:
        # heap_group_obj[1] — это прямоугольник кучи (heap_box)
        heap_cell.move_to(heap_group_obj[1].get_center())
        # теперь этот heap_cell (пока прозрачный) добавляем на сцену заранее
        self.add(heap_cell)

        # Подпись (caption) внизу экрана, но слегка приподнята,
        # чтобы не наезжать на границы и на "Опасно".
        caption = step_caption("").to_edge(DOWN)
        caption.shift(UP * 0.5)

        # === Шаг 1. Показать код ===
        self.play(Create(code_group), run_time=2.0)
        self.wait(0.5)

        # === Шаг 2. Показать стек и кучу ===
        self.play(
            FadeIn(stack_group_obj, run_time=1.5),
            FadeIn(heap_group_obj, run_time=1.5),
        )
        self.wait(0.5)

        cap1 = step_caption("У процесса есть стек (слева) и куча (справа). Это разные области памяти.")
        cap1.to_edge(DOWN)
        cap1.shift(UP * 0.5)
        self.play(Transform(caption, cap1), run_time=1.5)
        self.wait(2.0)

        # Подсветка переменной p в стеке
        p_highlight = SurroundingRectangle(
            p_box,
            color=RED,
            buff=0.12,
            stroke_width=4
        )
        self.play(Create(p_highlight), run_time=1.5)

        cap2 = step_caption("Стек: тут лежат локальные переменные функции main(). Здесь лежит p = 0x1000.")
        cap2.to_edge(DOWN)
        cap2.shift(UP * 0.5)
        self.play(Transform(caption, cap2), run_time=1.5)
        self.wait(2.0)

        # Подсветка строки с new
        code_highlight_alloc = SurroundingRectangle(
            code_group[1],
            color=YELLOW,
            buff=0.15,
            stroke_width=4
        )
        self.play(Create(code_highlight_alloc), run_time=1.5)
        self.wait(0.5)

        cap3 = step_caption("int* p = new int(5); — просим память в куче и кладём туда число 5.")
        cap3.to_edge(DOWN)
        cap3.shift(UP * 0.5)
        self.play(Transform(caption, cap3), run_time=1.5)
        self.wait(2.0)

        # === Шаг 3. Появление блока в куче (теперь по центру кучи) ===
        self.play(heap_cell.animate.set_opacity(1), run_time=1.5)

        cap4 = step_caption("В куче появилась ячейка по адресу 0x1000. В ней лежит 5.")
        cap4.to_edge(DOWN)
        cap4.shift(UP * 0.5)
        self.play(Transform(caption, cap4), run_time=1.5)
        self.wait(2.0)

        # === Шаг 4. Стрелка p -> куча ===
        ptr_arrow_grp = pointer_arrow_stack_to_heap(p_box, heap_cell[0], color_frame=ORANGE)
        self.play(Create(ptr_arrow_grp), run_time=1.5)

        cap5 = step_caption("Адрес этой ячейки (0x1000) записан в p. p указывает на память в куче.")
        cap5.to_edge(DOWN)
        cap5.shift(UP * 0.5)
        self.play(Transform(caption, cap5), run_time=1.5)
        self.wait(2.5)

        # === Шаг 5. Разыменование *p ===
        code_highlight_use = SurroundingRectangle(
            code_group[1],
            color=ORANGE,
            buff=0.15,
            stroke_width=4
        )

        p_focus = SurroundingRectangle(
            p_box,
            color=ORANGE,
            buff=0.12,
            stroke_width=4
        )

        heap_val_focus = SurroundingRectangle(
            heap_cell[1],  # сам текст "5"
            color=ORANGE,
            buff=0.12,
            stroke_width=4
        )

        self.play(
            ReplacementTransform(code_highlight_alloc, code_highlight_use),
            ReplacementTransform(p_highlight, p_focus),
            run_time=1.5
        )
        self.play(Create(heap_val_focus), run_time=1.5)

        cap6 = step_caption("*p: взять адрес из p → перейти в кучу → прочитать значение 5.")
        cap6.to_edge(DOWN)
        cap6.shift(UP * 0.5)
        self.play(Transform(caption, cap6), run_time=1.5)
        self.wait(2.0)

              # === Шаг 6. delete p ===
        code_highlight_delete = SurroundingRectangle(
            code_group[1],
            color=RED,
            buff=0.15,
            stroke_width=4
        )
        self.play(
            ReplacementTransform(code_highlight_use, code_highlight_delete),
            run_time=1.5
        )
        self.wait(0.5)

        cap7 = step_caption("delete p: освобождаем память — блок в куче удаляется.")
        cap7.to_edge(DOWN)
        cap7.shift(UP * 0.5)
        self.play(Transform(caption, cap7), run_time=1.5)
        self.wait(1.5)

        # убираем подсветку адреса и значения 5
        self.play(
            FadeOut(heap_val_focus, run_time=1.0),
            FadeOut(p_focus, run_time=1.0),
        )
        self.wait(0.3)

        # удаляем сам блок из кучи
        self.play(FadeOut(heap_cell, run_time=1.5))
        self.wait(0.8)

        # убираем стрелку p -> куча
        self.play(FadeOut(ptr_arrow_grp), run_time=1.0)
        self.wait(0.5)

        # убираем подсветку delete
        self.play(FadeOut(code_highlight_delete), run_time=1.0)
        self.wait(0.5)

        # === Шаг 7. Эффект "опасно": затемнение экрана + крупное предупреждение ===

        dark_bg = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            fill_color=BLACK,
            fill_opacity=0.75,
            stroke_width=0,
        )
        dark_bg.move_to(ORIGIN)

        # Текст предупреждения
        warn_text = Text(
            "ОПАСНО!\n"
            "Переменная p всё ещё хранит адрес 0x1000,\n"
            "но память по этому адресу уже освобождена.\n"
            "Это висячий указатель (dangling pointer).",
            font_size=32,
            color=RED,
            line_spacing=1.2
        )

        warn_box = SurroundingRectangle(
            warn_text,
            color=RED,
            buff=0.6,
            stroke_width=4
        )

        warn_group = VGroup(warn_box, warn_text)
        warn_group.move_to(ORIGIN)

        # Плавное появление фона, потом предупреждения
        self.play(FadeIn(dark_bg, run_time=1.5))
        self.play(FadeIn(warn_group, scale=0.8), run_time=2.0)

        self.wait(3.5)

        self.play(
            FadeOut(warn_group, run_time=1.5),
            FadeOut(dark_bg, run_time=1.5),
        )

        self.wait(1.0)
