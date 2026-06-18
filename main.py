import gradio as gr
from src.database import inicializar_banco
from src.agent import conversar
from src.rag import sincronizar_pdfs

# =====================================================
# INICIALIZAÇÃO
# =====================================================

inicializar_banco()
sincronizar_pdfs()

# =====================================================
# INTERFACE GRADIO
# =====================================================

def ver_tarefas_via_ia():
    resposta_ia = conversar("Jarvis, liste todas as minhas tarefas pendentes por favor.")
    return resposta_ia

def ver_agenda_via_ia():
    resposta_ia = conversar("Jarvis, o que eu tenho na minha agenda completa?")
    return resposta_ia

def interface_responder(mensagem, historico):
    resposta = conversar(mensagem)
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": resposta})
    return "", historico

if __name__ == "__main__":
    with gr.Blocks(title="Jarvis", fill_height=True) as interface:
        gr.Markdown("# ok JARVIS")
    
        with gr.Row():
            # LADO ESQUERDO: CHAT
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(height="700px")
                with gr.Row():
                    msg = gr.Textbox(placeholder="Fale com o Jarvis...", show_label=False, scale=4)
                    btn_enviar = gr.Button("Enviar", scale=1)

                msg.submit(interface_responder, [msg, chatbot], [msg, chatbot])
                btn_enviar.click(interface_responder, [msg, chatbot], [msg, chatbot])

            # LADO DIREITO: BOTÕES DE DADOS (VIA IA)
            with gr.Column(scale=1):
                gr.Markdown("### Consultas Rápidas via IA")
                btn_tarefas = gr.Button("📋 Tarefas")
                btn_agenda = gr.Button("📅 Agenda")
            
                visor = gr.Textbox(label="Resposta da IA", lines=18, interactive=False)
            
                btn_tarefas.click(ver_tarefas_via_ia, outputs=visor)
                btn_agenda.click(ver_agenda_via_ia, outputs=visor)

        print("Iniciando Jarvis...")
        interface.launch(theme="soft")