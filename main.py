import flet as ft import datetime import io import pandas as pd from supabase import create_client, Client

Supabase config

SUPABASE_URL = "https://ximwvadexnqwezptirvb.supabase.co" SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhpbXd2YWRleG5xd2V6cHRpcnZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDYzNTg1NDYsImV4cCI6MjA2MTkzNDU0Nn0.dpkTJVC01aNjyVAtA-SMzPBDgM98e1GHTesfrtfj_S8" supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

UNIDADES = ["kg", "g", "l", "ml", "un", "cx", "m", "cm"] FORNECEDORES = ["Fornecedor A", "Fornecedor B", "Fornecedor C"] ATIVO_OPCOES = ["Sim", "Não"]

def main(page: ft.Page): page.title = "Controle de Estoque" page.scroll = ft.ScrollMode.AUTO snackbar = ft.SnackBar(content=ft.Text("")) page.snack_bar = snackbar

selected_index = ft.Control(value=0)

def atualizar_pagina():
    page.controls.clear()
    if selected_index.value == 0:
        page.add(estoque_view())
    elif selected_index.value == 1:
        page.add(relatorios_view())
    elif selected_index.value == 2:
        page.add(ft.Text("Configurações (em breve)", size=24))

    page.add(
        ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=ft.icons.INVENTORY, label="Estoque"),
                ft.NavigationDestination(icon=ft.icons.INSERT_CHART, label="Relatórios"),
                ft.NavigationDestination(icon=ft.icons.SETTINGS, label="Configurações")
            ],
            selected_index=selected_index.value,
            on_change=lambda e: mudar_view(e.control.selected_index)
        )
    )
    page.update()

def mudar_view(index):
    selected_index.value = index
    atualizar_pagina()

def estoque_view():
    def ver_desativados(e):
        dados = supabase.table("estoque").select("*").eq("ativo", "Não").execute().data
        desativados = ft.DataTable(columns=[
            ft.DataColumn(label=ft.Text("Item")),
            ft.DataColumn(label=ft.Text("Unidade")),
            ft.DataColumn(label=ft.Text("Qtd. Atual")),
            ft.DataColumn(label=ft.Text("Validade")),
            ft.DataColumn(label=ft.Text("Fornecedor")),
            ft.DataColumn(label=ft.Text("Ações"))
        ], rows=[
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(d["item"])),
                ft.DataCell(ft.Text(d["unidade"])),
                ft.DataCell(ft.Text(str(d["qtd_atual"]))),
                ft.DataCell(ft.Text(d["validade"])),
                ft.DataCell(ft.Text(d["fornecedor"])),
                ft.DataCell(ft.IconButton(icon=ft.icons.RESTORE, tooltip="Reativar", on_click=lambda e, id=d["id"]: reativar_item(id)))
            ]) for d in dados
        ])),
                ft.DataCell(ft.Text(d["unidade"])),
                ft.DataCell(ft.Text(str(d["qtd_atual"]))),
                ft.DataCell(ft.Text(d["validade"])),
                ft.DataCell(ft.Text(d["fornecedor"]))
            ]) for d in dados
        ])

        def reativar_item(id):
        supabase.table("estoque").update({"ativo": "Sim"}).eq("id", id).execute()
        page.dialog = None
        snackbar.content.value = "Item reativado com sucesso."
        snackbar.open = True
        page.update()

        page.dialog = None
        atualizar_pagina()

    dialog = ft.AlertDialog(
            title=ft.Text("Itens Desativados"),
            content=ft.Container(content=desativados, width=600, height=400, padding=10, scroll=ft.ScrollMode.AUTO),
            actions=[ft.TextButton("Fechar", on_click=lambda e: page.dialog.close())]
        )
        page.dialog = dialog
        dialog.open = True
        page.update()
    item = ft.TextField(label="Item")
    unidade = ft.Dropdown(label="Unidade", options=[ft.dropdown.Option(u) for u in UNIDADES])
    qtd_atual = ft.TextField(label="Qtd. Atual", keyboard_type=ft.KeyboardType.NUMBER)
    qtd_minima = ft.TextField(label="Qtd. Mínima", keyboard_type=ft.KeyboardType.NUMBER)
    validade = ft.TextField(label="Validade (dd/mm/aaaa)")
    fornecedor = ft.Dropdown(label="Fornecedor", options=[ft.dropdown.Option(f) for f in FORNECEDORES])
    ativo = ft.Dropdown(label="Ativo", options=[ft.dropdown.Option(o) for o in ATIVO_OPCOES])

    tabela = ft.DataTable(columns=[
        ft.DataColumn(label=ft.Text("Item")),
        ft.DataColumn(label=ft.Text("Unidade")),
        ft.DataColumn(label=ft.Text("Qtd. Atual")),
        ft.DataColumn(label=ft.Text("Qtd. Mínima")),
        ft.DataColumn(label=ft.Text("Diferença")),
        ft.DataColumn(label=ft.Text("Validade")),
        ft.DataColumn(label=ft.Text("Fornecedor")),
        ft.DataColumn(label=ft.Text("Ações")),
    ], rows=[])

    def carregar_dados():
        tabela.rows.clear()
        dados = supabase.table("estoque").select("*").execute().data
        for d in dados:
            if d.get("ativo") == "Não":
                continue
            diff = float(d["qtd_atual"]) - float(d["qtd_minima"])
            tabela.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(d["item"])),
                    ft.DataCell(ft.Text(d["unidade"])),
                    ft.DataCell(ft.Text(str(d["qtd_atual"]))),
                    ft.DataCell(ft.Text(str(d["qtd_minima"]))),
                    ft.DataCell(ft.Text(f"{diff:.2f}")),
                    ft.DataCell(ft.Text(d["validade"])),
                    ft.DataCell(ft.Text(d["fornecedor"])),
                    ft.DataCell(ft.Row([
                        ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, id=d["id"]: confirmar_exclusao(id))
                    ]))
                ])
            )
        page.update()

    def confirmar_exclusao(id):
        def sim(e):
            supabase.table("estoque").delete().eq("id", id).execute()
            carregar_dados()
            page.dialog = None
            page.update()

        confirm = ft.AlertDialog(
            title=ft.Text("Confirmação"),
            content=ft.Text("Deseja excluir este item?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.dialog.close()),
                ft.TextButton("Sim", on_click=sim)
            ]
        )
        page.dialog = confirm
        confirm.open = True
        page.update()

    def cadastrar(e):
        if not all([item.value, unidade.value, qtd_atual.value, qtd_minima.value, validade.value, fornecedor.value, ativo.value]):
            snackbar.content.value = "Preencha todos os campos."
            snackbar.open = True
            page.update()
            return

        novo_item = {
            "item": item.value,
            "unidade": unidade.value,
            "qtd_atual": float(qtd_atual.value),
            "qtd_minima": float(qtd_minima.value),
            "validade": validade.value,
            "fornecedor": fornecedor.value,
            "ativo": ativo.value
        }
        supabase.table("estoque").insert(novo_item).execute()
        snackbar.content.value = "Item cadastrado com sucesso."
        snackbar.open = True
        page.update()
        item.value = unidade.value = qtd_atual.value = qtd_minima.value = validade.value = fornecedor.value = ativo.value = ""
        carregar_dados()

    carregar_dados()

    return ft.Column([
        ft.Text("Cadastro de Item", size=20, weight="bold"),
        item, unidade, qtd_atual, qtd_minima, validade, fornecedor, ativo,
        ft.ElevatedButton("Cadastrar", on_click=cadastrar),
        ft.Row([
            ft.Text("Estoque Atual", size=18, expand=True),
            ft.IconButton(icon=ft.icons.VIEW_LIST, tooltip="Ver Desativados", on_click=ver_desativados)
        ]),
        tabela
    ])

def relatorios_view():
    dados = supabase.table("estoque").select("*").execute().data
    df = pd.DataFrame(dados)

    qtd_total = df["qtd_atual"].sum() if not df.empty else 0
    itens_abaixo_min = df[df["qtd_atual"] < df["qtd_minima"]].shape[0]
    vencendo = df[df["validade"].apply(lambda d: datetime.datetime.strptime(d, "%d/%m/%Y") <= datetime.datetime.now() + datetime.timedelta(days=30))]

    def gerar_excel(e):
        output = io.BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        page.launch_url("data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64," + output.getvalue().decode("latin1"), web_window_name="_blank")

    return ft.Column([
        ft.Text("Relatórios de Estoque", size=24, weight="bold"),
        ft.Row([
            ft.Container(content=ft.Column([
                ft.Text("Qtd. Total em Estoque", weight="bold"),
                ft.Text(f"{qtd_total:.2f}")
            ]), bgcolor=ft.colors.GREEN_100, padding=10, border_radius=10),
            ft.Container(content=ft.Column([
                ft.Text("Itens abaixo da Qtd. Mínima", weight="bold"),
                ft.Text(f"{itens_abaixo_min}")
            ]), bgcolor=ft.colors.RED_100, padding=10, border_radius=10),
            ft.Container(content=ft.Column([
                ft.Text("Vencendo em até 30 dias", weight="bold"),
                ft.Text(f"{len(vencendo)}")
            ]), bgcolor=ft.colors.ORANGE_100, padding=10, border_radius=10),
        ], scroll=ft.ScrollMode.AUTO),
        ft.Divider(),
        ft.ElevatedButton("Exportar para Excel", icon=ft.icons.DOWNLOAD, on_click=gerar_excel),
    ])

atualizar_pagina()

ft.app(target=main)
