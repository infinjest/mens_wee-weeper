import common_logics as cl


def show_open(field, canvas, droplets_img, eggplant_img, transp_sq, mode):
    # getting tables "(cell's coords) -> number of canvas obj" for img and txt layer
    img_table = cl.get_table(101)
    txt_table = cl.get_table(201)

    for i in range(field.n):
        for j in range(field.n):
            cell = field.field[i][j]
            if mode == "show":
                if not cell.is_open:
                    canvas.itemconfigure(img_table[(i, j)], image=droplets_img if cell.is_tagged else transp_sq)
                else:
                    if cell.is_mine:
                        canvas.itemconfigure(img_table[(i, j)], image=eggplant_img)
                    elif cell.is_tagged:
                        canvas.itemconfigure(img_table[(i, j)], image=transp_sq)
                        field.tags -= 1
                    else:
                        canvas.itemconfigure(txt_table[(i, j)], text=f"{cell.number}" if cell.number != 0 else "")
            elif mode == "open":
                if cell.is_tagged:
                    canvas.itemconfigure(img_table[(i, j)], image=transp_sq if not cell.is_mine else eggplant_img)
                else:
                    if not cell.is_mine:
                        canvas.itemconfigure(txt_table[(i, j)], text=f"{cell.number}" if cell.number != 0 else "")
                    else:
                        canvas.itemconfigure(img_table[(i, j)], image=eggplant_img)
                fill_opened_cells(field, canvas, all=True)
        print()

def fill_opened_cells(field, canvas, all):
    # getting table for cells layer (in order to change their fill)
    cells_table = cl.get_table(1)

    for i in range(field.n):
        for j in range(field.n):
            cell = field.field[i][j]
            if not all:
                if cell.is_open:
                    # fill in red the cell which was blown up
                    canvas.itemconfigure(cells_table[(i, j)], fill="#fa0202" if cell.is_mine else '#56b6c2')
            if all:
                if cell.is_tagged:
                    # visualizing the correctness of flags installation
                    canvas.itemconfigure(cells_table[(i, j)], fill="#76f1bc" if cell.is_mine else "#ffacb6")
                else:
                    # the cell with the mine that the player blew up on remained red
                    if canvas.itemcget(cells_table[(i, j)], option="fill") != "#fa0202":
                        canvas.itemconfigure(cells_table[(i, j)], fill='#56b6c2')