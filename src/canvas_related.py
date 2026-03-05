from common_logics import get_table


target_cell, prev_cell = None, None

def show_open(field, canvas, droplets_img, eggplant_img, transp_sq, mode):
    # getting tables "(cell's coords) -> number of canvas obj" for img and txt layer
    img_table = get_table(101)
    txt_table = get_table(201)

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
    cells_table = get_table(1)

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

# event handler - "cursor hovers over a closed cell"
def on_motion(event, canvas, cells, field):
    #=^.^=
    global target_cell, prev_cell
    cell_table = get_table(1, True)
    for key in cells:
        if key[0][0] < event.x < key[0][1] and key[1][0] < event.y < key[1][1]:
            i, j = cell_table[cells[key]]
            cell = field.field[i][j]
            if cell:
                # get all objects under the cursor (in stack order, bottom to top)
                objects_under = canvas.find_overlapping(event.x, event.y, event.x, event.y)

                # looking for the first object with the tag "cell"
                for obj in objects_under:
                    tags = canvas.gettags(obj)
                    if "cell" in tags:
                        target_cell = obj
                        break

                # if the target object is found and it has changed
                if target_cell and target_cell != prev_cell:
                    # remove the fill from the previous one
                    if prev_cell and canvas.itemcget(prev_cell, option="fill") != '#56b6c2':
                        canvas.itemconfigure(prev_cell, fill='light blue')
                    # filling the next one, moving on to the next one
                    if canvas.itemcget(target_cell, option="fill") != '#56b6c2':
                        canvas.itemconfigure(target_cell, fill='light grey')
                        prev_cell = target_cell
            else:
                on_leaving(event, canvas, cells)

# if the cursor is out of the field, return the fill to its original state        
def on_leaving(event, canvas, cells):
    global target_cell, prev_cell
    for value in cells.values():
        if canvas.itemcget(value, option="fill") == "light grey":
            canvas.itemconfigure(value, fill='light blue')
            prev_cell = target_cell = None