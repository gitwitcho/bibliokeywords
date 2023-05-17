

def highlight_selected_text(text: str, 
                            strings: Union[List[str], str], 
                            colour: str, 
                            partial: bool = True, 
                            i_row: Optional[int] = None
                            ) -> str:
    text = str(text)

    if isinstance(strings, str):
        strings = [strings]
    
    if i_row and (i_row % 100 == 0) and (logger.get_level() == logging.INFO): # print row index
        print(f'{i_row}', end = '\r')

    if len(strings) == 0:
        return text
    
    if (len(strings) == 1) and (strings[0] == ""):
        return text

    for k in strings:
        if partial: # highlight partial and full matches
            # pattern = r"\b\w*{}+\w*\b".format(k)
            pattern = r"(?<!>)\b\w*{}+\w*\b(?!<)".format(k)
            text = re.sub(pattern, lambda match: f'<span style="color: {colour}; font-weight: bold">{match.group()}</span>', text, flags = re.IGNORECASE)
        else:   # highlight full matches only
            # pattern = r"(?i)\b"+k+r"[\w-]*"
            pattern = r"(?i)(?<!>)\b"+k+r"[\w-]*\b(?!<)"
            text = re.sub(pattern, lambda match: f'<span style="color: {colour}; font-weight: bold">{match.group()}</span>', text)

    return text


def colour_name_to_hex(colour_name):
    # See the colour names here: https://www.w3.org/TR/SVG11/types.html#ColorKeywords

    try:
        # Get RGB value for the color name
        rgb = webcolors.name_to_rgb(colour_name)

        # Convert RGB to hex code
        hex_code = webcolors.rgb_to_hex(rgb)

        return hex_code
    except:
        raise ValueError(f"The colour {colour_name} does not exist")


def get_excel_column(number):
    column = ""
    while number > 0:
        number, remainder = divmod(number - 1, 26)
        column = chr(65 + remainder) + column
    return column


def excel_highlights_builder(biblio_highlights_df: pd.DataFrame,
                             excel_params: Optional[Any]) -> Workbook:

    # FIXME: This needs the lxml package installed for Workbook.save to work. Add that to the requirements.txt

    excel_sheet_name = 'Highlights' # default name for the new Excel sheet with the highlights
    excel_zoom = 100    # default zoom of the sheet
    excel_freeze_panes = None   # default freeze for horizontal panes
    excel_cols = None
    excel_highlighted_cols = None

    default_width = 15
    default_wrap = False

    # Unpack the parameters
    if isinstance(excel_params, Dict):
        excel_cols = excel_params.get('cols', None)
        excel_sheet_name = excel_params.get('sheet_name', None)
        excel_zoom = excel_params.get('zoom', excel_zoom)
        excel_freeze_panes = excel_params.get('freeze_panes', excel_freeze_panes)
        excel_highlighted_cols = excel_params.get('highlighted_cols', None)
    elif excel_params != None:
        raise ValueError(f"The function argument excel_params has to be a dictionary")
    
    formatted_cols = []
    remaining_cols = []

    # Get the columns to be added first (the remaining columns are added as-is to the Excel sheet)
    if isinstance(excel_cols, List):
        formatted_cols = [d['col'] for d in excel_cols if d['col'] in biblio_highlights_df.columns]
        remaining_cols = [col for col in biblio_highlights_df.columns if col not in formatted_cols]
    elif excel_cols == None:  # if no columns have been provided in excel_params, use all columns from biblio_highlights_df
        remaining_cols = biblio_highlights_df.columns
    else:
        raise ValueError(f"The item 'excel_cols' in the dictionary has to be a list")

    # Reorder the columns in biblio_highlights_df
    reorder_cols = formatted_cols + remaining_cols
    biblio_highlights_df = biblio_highlights_df[reorder_cols]

    # Create a new workbook
    wb = Workbook()

    # Create a new sheet
    ws = wb.create_sheet(excel_sheet_name)

    # Remove the default sheet
    if wb["Sheet"]:
        wb.remove(wb["Sheet"])

    # Make a copy of titles_highlights_df
    tak_excel_df = biblio_highlights_df.copy()

    # Excel column headers
    for j, col in enumerate(formatted_cols):
        # header = str(tak_excel_df.columns[j])
        header = col

        if excel_cols is not None:
            header = next((col_info.get('heading', col) for col_info in excel_cols if col_info['col'] == col), col)

        ws.cell(row = 1, column = j + 1, value = header).font = Font(bold = True)

    cursor = len(formatted_cols)

    for j, col in enumerate(remaining_cols):
        header = col

        if excel_cols is not None:
            header = next((col_info.get('heading', col) for col_info in excel_cols if col_info['col'] == col), col)

        ws.cell(row = 1, column = j + cursor + 1, value = header).font = Font(bold = True)

    # Apply findall() to split a string at '<span.../span>'
    def split_string_at_span(string):
        lst = re.findall(r"(.*?)(<span.*?/span>|$)", string)
        lst = [elem for tup in lst for elem in tup]
        lst = [x for x in lst if x.strip()]
        return lst

    def replace_span_with_textblock(lst: List[str]) -> List[str]:
        is_prev_kw = False  # need to add a space between two consecutive keywords
        rich_text_lst = []

        for string in lst:
            if string.startswith('<span'):
                colour_name = re.findall(r'color: (\w+)', string)[0] if re.findall(r'color: (\w+)', string) else None
                colour_hex = '00' + colour_name_to_hex(colour_name = colour_name)[1:]
                # span_string = '<span style="color: {}; font-weight: bold">'.format(colour_name)
                text = (' ' if is_prev_kw else '') + string.split('>')[1].split('<')[0]
                text_block = TextBlock(InlineFont(b = True, color = colour_hex), text)  # type: ignore (the Pylance issue is caused by the TextBlock constructor typing)
                rich_text_lst.append(text_block)
                is_prev_kw = True
            else:
                rich_text_lst.append(string)
                is_prev_kw = False

        return rich_text_lst

    if excel_highlighted_cols is not None:
        excel_highlighted_cols = [col for col in excel_highlighted_cols if col in biblio_highlights_df.columns]

        for col in excel_highlighted_cols:
            # Create a list of each cell content by splitting at '<span...>some text</span>' using findall()
            tak_excel_df[col] = tak_excel_df[col].apply(split_string_at_span)

            # Replace all '<span...>some text</span>' with the results of calling TextBlock(bold_red, 'some text')
            tak_excel_df[col] = tak_excel_df[col].apply(replace_span_with_textblock)

    numeric_cols = biblio_highlights_df.select_dtypes(include = "number").columns.tolist()

    # Loop through rows and columns of the dataframe
    for i in range(len(tak_excel_df)):
        for col in tak_excel_df.columns:
            j = tak_excel_df.columns.get_loc(col)

            if col in excel_highlighted_cols:
                rs = CellRichText(tak_excel_df.iloc[i, j])  # type: ignore - not sure how to avoid the Pylance typing warning
            elif col in numeric_cols:
                # rs = str(tak_excel_df.iloc[i, j])
                rs = tak_excel_df.iloc[i, j]
            else:
                rs = str(tak_excel_df.iloc[i, j])

            ws.cell(row = i + 2, column = j + 1, value = rs)

    for idx, col in enumerate(formatted_cols):
        col_letter = get_excel_column(idx + 1)
        width = default_width
        wrap = default_wrap

        if excel_cols is not None:
            width = next((col_info.get('width', default_width) for col_info in excel_cols if col_info['col'] == col), default_width)
            wrap = next((col_info.get('wrap', default_wrap) for col_info in excel_cols if col_info['col'] == col), default_wrap)

        ws.column_dimensions[col_letter].width = width

        for cell in ws[col_letter]:
            cell.alignment = Alignment(wrap_text = wrap)

    ws.sheet_view.zoomScale = excel_zoom

    if excel_freeze_panes:
        ws.freeze_panes = excel_freeze_panes

    return wb


def highlight_keywords(biblio_df: pd.DataFrame,
                        highlight_params: List[Dict[str, Union[List[str], str]]],
                        html_cols: Optional[List] = None,
                        xlsx_cols: Optional[List] = None,
                        excel_params: Optional[Any] = None
                        ) -> Tuple[Optional[HTML], Optional[Workbook]]:
    biblio_highlights_df = biblio_df.copy()

    highlighted_cols = []

    for param in highlight_params:
        if not all([key in param for key in ['strings', 'targets']]):
            raise ValueError(f"The key 'strings' or 'targets' is missing in the parameter dictionary")
        
        if 'colour' not in param:
            colour = 'red'
        else:
            colour = param.get('colour')

        if isinstance(param['strings'], list):
            strings = param.get('strings', [])
        else:
            strings = str(param.get('strings'))

        if isinstance(param['targets'], list):
            targets = param.get('targets', [])
        else:
            targets = [param.get('targets')]

        # Highlight the strings provided in param
        for target in targets:
            if target in biblio_highlights_df.columns:
                highlighted_cols.append(target)
                print(f'Highlighting strings in {colour} in the {target}...')
                biblio_highlights_df[target] = biblio_highlights_df \
                    .apply(lambda x: highlight_selected_text(
                            text = x[target], 
                            strings = strings, 
                            colour = str(colour), 
                            i_row = biblio_highlights_df.index.get_loc(x.name)), axis = 1)

    html_out = None
    xlsx_out = None

    if html_cols != None:
        if html_cols == []:
            html_out = HTML(biblio_highlights_df.to_html(escape = False))
        else:
             html_out = HTML(biblio_highlights_df[html_cols].to_html(escape = False))

    if excel_params != None:
        excel_params['highlighted_cols'] = list(set(highlighted_cols))

    if xlsx_cols != None:
        if xlsx_cols == []:
            xlsx_cols = list(biblio_highlights_df.columns)
        
        xlsx_out = excel_highlights_builder(biblio_highlights_df = biblio_highlights_df[xlsx_cols],
                                            excel_params = excel_params)
    else:
        xlsx_out = excel_highlights_builder(biblio_highlights_df = biblio_highlights_df,
                                            excel_params = excel_params)

    return html_out, xlsx_out

