import discord
from discord.ext import commands, tasks
from discord import Embed, Interaction, app_commands
import json
import os
try:
    from dotenv import load_dotenv
    # load default .env first
    load_dotenv()
    # If BOT_TOKEN not set, attempt common alternative filenames (typo like .ev)
    if not os.environ.get('BOT_TOKEN'):
        # try '.ev' in project root (some users accidentally name it .ev)
        try:
            load_dotenv('.ev')
        except Exception:
            pass
    # final attempt: explicit path next to this file
    if not os.environ.get('BOT_TOKEN'):
        try:
            load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
        except Exception:
            pass
    # Print presence (not value) to help debug when running locally
    try:
        print(f"[DEBUG] BOT_TOKEN set in env? {'YES' if os.environ.get('BOT_TOKEN') else 'NO'}")
    except Exception:
        pass
except Exception:
    # python-dotenv is optional; if not installed, environment variables must be set externally
    pass
from datetime import datetime, timedelta
import random

# Single bot instance with proper intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.tree.command(name="admin_remover_item", description="👑 [ADMIN] Remover um item de um usuário")
@app_commands.checks.has_permissions(administrator=True)
async def admin_remover_item(interaction: discord.Interaction, usuario: discord.Member, item: str):
    user_data = get_user_data(usuario.id)
    item = item.lower().replace(" ", "_")
    
    if item not in user_data["inventario"]:
        await interaction.response.send_message(f"{EMOJIS['erro']} {usuario.display_name} não possui este item!", ephemeral=True)
        return
    
    del user_data["inventario"][item]
    save_data(data)
    
    embed = discord.Embed(
        title=f"{EMOJIS['sucesso']} Item Removido",
        description=f"**{item.replace('_', ' ').title()}** foi removido de {usuario.display_name}",
        color=discord.Color.red()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="admin_reset", description="👑 [ADMIN] Resetar dados de um usuário")
@app_commands.checks.has_permissions(administrator=True)
async def admin_reset(interaction: discord.Interaction, usuario: discord.Member):
    if str(usuario.id) in data:
        del data[str(usuario.id)]
        save_data(data)
    
    embed = discord.Embed(
        title=f"{EMOJIS['sucesso']} Dados Resetados",
        description=f"Os dados de {usuario.display_name} foram resetados!",
        color=discord.Color.red()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="admin_set_nivel", description="👑 [ADMIN] Definir nível de um usuário")
@app_commands.checks.has_permissions(administrator=True)
async def admin_set_nivel(interaction: discord.Interaction, usuario: discord.Member, nivel: int):
    user_data = get_user_data(usuario.id)
    user_data["nivel"] = max(1, nivel)
    save_data(data)
    
    embed = discord.Embed(
        title=f"{EMOJIS['estrela']} Nível Alterado",
        description=f"{usuario.display_name} agora é **Nível {nivel}**!",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="admin_set_xp", description="👑 [ADMIN] Definir XP de um usuário")
@app_commands.checks.has_permissions(administrator=True)
async def admin_set_xp(interaction: discord.Interaction, usuario: discord.Member, xp: int):
    user_data = get_user_data(usuario.id)
    user_data["xp"] = max(0, xp)
    save_data(data)
    
    embed = discord.Embed(
        title=f"{EMOJIS['estrela']} XP Alterado",
        description=f"{usuario.display_name} agora tem **{xp} XP**!",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="admin_set_reputacao", description="👑 [ADMIN] Definir reputação de um usuário")
@app_commands.checks.has_permissions(administrator=True)
async def admin_set_reputacao(interaction: discord.Interaction, usuario: discord.Member, reputacao: int):
    user_data = get_user_data(usuario.id)
    user_data["reputacao"] = reputacao
    save_data(data)
    
    embed = discord.Embed(
        title=f"{EMOJIS['diamante']} Reputação Alterada",
        description=f"{usuario.display_name} agora tem **{reputacao}** de reputação!",
        color=discord.Color.purple()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="admin_set_trabalho", description="👑 [ADMIN] Definir trabalho de um usuário")
@app_commands.checks.has_permissions(administrator=True)
async def admin_set_trabalho(interaction: discord.Interaction, usuario: discord.Member, trabalho: str):
    user_data = get_user_data(usuario.id)
    trabalho = trabalho.lower()
    
    if trabalho not in TRABALHOS and trabalho != "nenhum":
        await interaction.response.send_message(f"{EMOJIS['erro']} Trabalho não encontrado! Use: {', '.join(TRABALHOS.keys())}", ephemeral=True)
        return
    
    user_data["trabalho"] = None if trabalho == "nenhum" else trabalho
    save_data(data)
    
    embed = discord.Embed(
        title=f"{EMOJIS['trabalho']} Trabalho Alterado",
        description=f"{usuario.display_name} agora trabalha como **{trabalho.title() if trabalho != 'nenhum' else 'Desempregado'}**!",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="admin_economia", description="👑 [ADMIN] Ver estatísticas gerais da economia")
@app_commands.checks.has_permissions(administrator=True)
async def admin_economia(interaction: discord.Interaction):
    total_usuarios = len(data)
    dinheiro_circulacao = sum(u["carteira"] + u["banco"] for u in data.values())
    media_patrimonio = dinheiro_circulacao // total_usuarios if total_usuarios > 0 else 0
    
    aneis_supremos = sum(1 for u in data.values() if "anel_supremo" in u["inventario"])
    vips_ativos = sum(1 for u in data.values() if u.get("vip"))
    
    embed = discord.Embed(
        title=f"{EMOJIS['grafico']} Estatísticas da Economia",
        color=discord.Color.purple()
    )
    embed.add_field(name="👥 Total de Usuários", value=f"**{total_usuarios}**", inline=True)
    embed.add_field(name="💰 Dinheiro em Circulação", value=f"**R$ {dinheiro_circulacao:,}**", inline=True)
    embed.add_field(name="📊 Patrimônio Médio", value=f"**R$ {media_patrimonio:,}**", inline=True)
    embed.add_field(name="💍 Portadores do Anel Supremo", value=f"**{aneis_supremos}**", inline=True)
    embed.add_field(name="🌟 VIPs Ativos", value=f"**{vips_ativos}**", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="admin_ver_inventario", description="👑 [ADMIN] Ver inventário de um usuário")
@app_commands.checks.has_permissions(administrator=True)
async def admin_ver_inventario(interaction: discord.Interaction, usuario: discord.Member):
    user_data = get_user_data(usuario.id)
    
    embed = discord.Embed(
        title=f"🔍 Inventário de {usuario.display_name}",
        color=discord.Color.blue()
    )
    
    if not user_data["inventario"]:
        embed.description = "Inventário vazio."
    else:
        itens_texto = ""
        for item in user_data["inventario"]:
            if item in LOJA:
                info = LOJA[item]
                itens_texto += f"{info['emoji']} **{item.replace('_', ' ').title()}**\n"
            elif item in MERCADO_NEGRO:
                info = MERCADO_NEGRO[item]
                itens_texto += f"{info['emoji']} **{item.replace('_', ' ').title()}** (Mercado Negro)\n"
        embed.description = itens_texto
    
    embed.add_field(name="💰 Carteira", value=f"R$ {user_data['carteira']:,}", inline=True)
    embed.add_field(name="🏦 Banco", value=f"R$ {user_data['banco']:,}", inline=True)
    embed.add_field(name="⭐ Nível", value=f"{user_data['nivel']}", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="admin_listar_itens", description="👑 [ADMIN] Ver todos os itens disponíveis")
@app_commands.checks.has_permissions(administrator=True)
async def admin_listar_itens(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📦 Todos os Itens do Sistema",
        description="Lista completa de itens que podem ser dados aos jogadores:\n",
        color=discord.Color.gold()
    )
    
    loja_texto = ""
    for item, info in LOJA.items():
        loja_texto += f"{info['emoji']} `{item}`"
        if info.get("secreto"):
            loja_texto += " ⚠️ **SECRETO**"
        loja_texto += f"\n"
    
    embed.add_field(name="🛍️ Loja Comum", value=loja_texto, inline=False)
    
    mercado_texto = ""
    for item, info in MERCADO_NEGRO.items():
        mercado_texto += f"{info['emoji']} `{item}`\n"
    
    embed.add_field(name="🎭 Mercado Negro", value=mercado_texto, inline=False)
    
    embed.set_footer(text="Use: /admin_dar_item <usuario> <nome_do_item>")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="admin_limpar_economia", description="👑 [ADMIN] ⚠️ RESETAR TODA A ECONOMIA")
@app_commands.checks.has_permissions(administrator=True)
async def admin_limpar_economia(interaction: discord.Interaction, confirmacao: str):
    if confirmacao != "CONFIRMAR":
        embed = discord.Embed(
            title=f"{EMOJIS['alerta']} Confirmação Necessária",
            description="Este comando irá **DELETAR TODOS OS DADOS** da economia!\n\nPara confirmar, use:\n`/admin_limpar_economia confirmacao:CONFIRMAR`",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    data.clear()
    save_data(data)
    
    embed = discord.Embed(
        title=f"{EMOJIS['sucesso']} Economia Resetada",
        description="**TODOS** os dados da economia foram deletados!",
        color=discord.Color.dark_red()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="admin_dar_dinheiro_todos", description="👑 [ADMIN] Dar dinheiro para todos do servidor")
@app_commands.checks.has_permissions(administrator=True)
async def admin_dar_dinheiro_todos(interaction: discord.Interaction, quantia: int):
    contador = 0
    for member in interaction.guild.members:
        if not member.bot:
            user_data = get_user_data(member.id)
            user_data["carteira"] += quantia
            contador += 1
    
    save_data(data)
    
    embed = discord.Embed(
        title=f"{EMOJIS['presente']} Dinheiro Distribuído!",
        description=f"**R$ {quantia:,}** foram dados para **{contador} usuários**!",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="admin_ajuda", description="👑 [ADMIN] Ver todos os comandos administrativos")
@app_commands.checks.has_permissions(administrator=True)
async def admin_ajuda(interaction: discord.Interaction):
    embed = discord.Embed(
        title="👑 Comandos Administrativos",
        description="Lista completa de comandos para administradores:\n",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="💰 Economia",
        value=(
            "`/admin_add` - Adicionar dinheiro\n"
            "`/admin_remove` - Remover dinheiro\n"
            "`/admin_dar_dinheiro_todos` - Dar dinheiro a todos\n"
            "`/admin_economia` - Ver estatísticas"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🎒 Itens",
        value=(
            "`/admin_dar_item` - Dar item\n"
            "`/admin_remover_item` - Remover item\n"
            "`/admin_listar_itens` - Listar todos os itens\n"
            "`/admin_ver_inventario` - Ver inventário de alguém"
        ),
        inline=False
    )
    
    embed.add_field(
        name="👤 Perfil",
        value=(
            "`/admin_set_nivel` - Definir nível\n"
            "`/admin_set_xp` - Definir XP\n"
            "`/admin_set_reputacao` - Definir reputação\n"
            "`/admin_set_trabalho` - Definir trabalho\n"
            "`/admin_reset` - Resetar dados"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🌟 VIP",
        value=(
            "`/admin_dar_vip` - Dar VIP a alguém\n"
            "`/admin_remover_vip` - Remover VIP\n"
            "`/admin_listar_vips` - Ver todos os VIPs\n"
            "`/admin_configurar_cargo_vip` - Configurar cargo VIP\n"
            "`/admin_painel_vip` - Criar painel público de VIP"
        ),
        inline=False
    )
    
    embed.add_field(
        name="⚠️ Perigoso",
        value="`/admin_limpar_economia` - Resetar TUDO (requer confirmação)",
        inline=False
    )
    
    embed.set_footer(text="⚡ Use com responsabilidade!")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ============ TRATAMENTO DE ERROS ============

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        embed = discord.Embed(
            title=f"{EMOJIS['erro']} Acesso Negado",
            description="Você precisa ser **Administrador** para usar este comando!",
            color=discord.Color.red()
        )
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"Erro ao enviar mensagem de erro: {e}")
    else:
        print(f"Erro no comando: {error}")

# ============ INICIAR BOT ============

# O token deve ser fornecido via variável de ambiente BOT_TOKEN para segurança.

"""
===========================================
📝 BOT DE ECONOMIA + VIP - ASTRAL ROLEPLAY
===========================================

✅ SISTEMA COMPLETO IMPLEMENTADO:
- 15+ comandos de economia
- Sistema VIP com 5 planos
- Loja interativa
- Celular virtual (Play Store, Mercado Negro, Banco)
- Trabalhos com progressão de nível
- Jogos de azar (apostar, investir, crime, roubar)
- 20+ comandos administrativos

🌟 COMANDOS VIP:
- /loja_vip - Comprar VIP com dinheiro do bot
- /vip - Ver status VIP
- /admin_dar_vip - Admin dar VIP gratuitamente
- /admin_remover_vip - Admin remover VIP
- /admin_listar_vips - Ver todos os VIPs
- /admin_configurar_cargo_vip - Vincular cargos do Discord
- /admin_painel_vip - Criar painel público bonito

⚙️ CONFIGURAÇÃO DOS CARGOS VIP:

1. Ative o Modo Desenvolvedor no Discord:
   Configurações > Avançado > Modo Desenvolvedor

2. Copie o ID do cargo:
   Clique direito no cargo > Copiar ID

3. Configure no Discord:
   /admin_configurar_cargo_vip vip:alpha cargo_id:SEU_ID_AQUI

Exemplo:
   /admin_configurar_cargo_vip vip:alpha cargo_id:1234567890123456789
   /admin_configurar_cargo_vip vip:beta cargo_id:9876543210987654321
   /admin_configurar_cargo_vip vip:omega cargo_id:1111111111111111111
   /admin_configurar_cargo_vip vip:diamond cargo_id:2222222222222222222
   /admin_configurar_cargo_vip vip:diamond2 cargo_id:3333333333333333333

💡 DICAS:
- Use /ajuda para ver todos os comandos
- Use /admin_ajuda para comandos administrativos
- Jogadores compram VIP com dinheiro do bot
- Admin pode dar VIP gratuitamente
- Cargos são atribuídos automaticamente

⚠️ IMPORTANTE:
- NUNCA exponha seu token publicamente
- Regenere o token se foi exposto
- Mantenha backups do arquivo economy_data.json

🚀 PRONTO PARA USO!
"""

@bot.tree.command(name="roubar", description="🎭 Tente roubar dinheiro de alguém (arriscado!)")
async def roubar(interaction: discord.Interaction, vitima: discord.Member):
    user_data = get_user_data(interaction.user.id)
    vitima_data = get_user_data(vitima.id)
    
    if vitima.id == interaction.user.id:
        await interaction.response.send_message(f"{EMOJIS['erro']} Você não pode roubar a si mesmo!", ephemeral=True)
        return
    
    if user_data["ultimo_roubo"]:
        ultimo = datetime.fromisoformat(user_data["ultimo_roubo"])
        if datetime.now() - ultimo < timedelta(hours=2):
            tempo_restante = timedelta(hours=2) - (datetime.now() - ultimo)
            horas = tempo_restante.seconds // 3600
            minutos = (tempo_restante.seconds % 3600) // 60
            await interaction.response.send_message(f"{EMOJIS['alerta']} Aguarde {horas}h {minutos}min para roubar novamente!", ephemeral=True)
            return
    
    if vitima_data["carteira"] < 100:
        await interaction.response.send_message(f"{EMOJIS['erro']} {vitima.display_name} não tem dinheiro suficiente na carteira!", ephemeral=True)
        return
    
    sucesso = random.random() > 0.5
    
    if sucesso:
        quantia = random.randint(50, min(vitima_data["carteira"], 1000))
        vitima_data["carteira"] -= quantia
        user_data["carteira"] += quantia
        user_data["reputacao"] -= 5
        
        embed = discord.Embed(
            title=f"{EMOJIS['roubou']} Roubo Bem-Sucedido!",
            description=f"Você conseguiu roubar **R$ {quantia:,}** de {vitima.display_name}!\n\n⚠️ Sua reputação diminuiu.",
            color=discord.Color.green()
        )
    else:
        multa = random.randint(200, 500)
        user_data["carteira"] -= min(multa, user_data["carteira"])
        user_data["reputacao"] -= 10
        
        embed = discord.Embed(
            title=f"{EMOJIS['alerta']} Você foi Pego!",
            description=f"Sua tentativa de roubo falhou!\n\n**Multa:** R$ {multa:,}\n⚠️ Sua reputação diminuiu significativamente.",
            color=discord.Color.red()
        )
    
    user_data["ultimo_roubo"] = datetime.now().isoformat()
    save_data(data)
    await interaction.response.send_message(embed=embed)


# ============ ANEL SUPREMO ============
anel = app_commands.Group(name="anel", description="Poderes do Anel Supremo")


@anel.command(name="criar", description="💫 Criar dinheiro do nada (apenas para portadores do Anel Supremo).")
async def anel_criar(interaction: discord.Interaction, quantia: int):
    user_data = get_user_data(interaction.user.id)

    # Verifica se o usuário possui o anel
    if "anel_supremo" not in user_data.get("inventario", {}):
        await interaction.response.send_message(f"{EMOJIS['erro']} Você não possui o Anel Supremo!", ephemeral=True)
        return

    # Checa cooldown diário (um uso por subcomando)
    hoje = datetime.now().date().isoformat()
    if user_data.get("anel_ultimo_uso_criar") == hoje:
        await interaction.response.send_message(f"{EMOJIS['alerta']} Você já usou /anel criar hoje. Tente novamente amanhã.", ephemeral=True)
        return

    if quantia <= 0:
        await interaction.response.send_message(f"{EMOJIS['erro']} Quantia inválida!", ephemeral=True)
        return

    MAX_DIARIO = 500_000
    if quantia > MAX_DIARIO:
        await interaction.response.send_message(f"{EMOJIS['erro']} Quantia excede o limite diário de R$ {MAX_DIARIO:,}.", ephemeral=True)
        return

    # Aplica criação do dinheiro
    user_data["carteira"] += quantia
    user_data["anel_ultimo_uso_criar"] = hoje
    save_data(data)

    embed = discord.Embed(
        title=f"{EMOJIS['foguete']} Poder Liberado!",
        description=(f"🌌 O universo se curva diante do Anel Supremo. {interaction.user.mention} criou **R$ {quantia:,}** do nada!\n\n"
                     "⚠️ Use com sabedoria — o equilíbrio pode cobrar um preço."),
        color=discord.Color.gold(),
        timestamp=datetime.now()
    )
    embed.set_author(name=f"{interaction.user.display_name} — Anel Supremo", icon_url=interaction.user.display_avatar.url)
    embed.add_field(name="Quantia Criada", value=f"R$ {quantia:,}", inline=True)
    embed.add_field(name="Limite Diário", value=f"R$ {MAX_DIARIO:,}", inline=True)
    embed.set_footer(text="Poder do Anel — use com responsabilidade")
    await interaction.response.send_message(embed=embed)

    # Log em canal de moderação (se configurado)
    try:
        log_channel = bot.get_channel(1398712093238235237)
        if not log_channel:
            try:
                log_channel = await bot.fetch_channel(1398712093238235237)
            except Exception:
                log_channel = None

        if log_channel:
            log_embed = discord.Embed(
                title="Anel Supremo — Criar",
                description=f"{interaction.user.mention} usou `/anel criar {quantia}`",
                color=discord.Color.gold(),
                timestamp=datetime.now()
            )
            log_embed.add_field(name="Executor", value=interaction.user.mention, inline=True)
            log_embed.add_field(name="Quantia", value=f"R$ {quantia:,}", inline=True)
            log_embed.add_field(name="Servidor", value=interaction.guild.name if interaction.guild else "Direto/DM", inline=False)
            await log_channel.send(embed=log_embed)
    except Exception as e:
        print(f"Erro ao enviar log do Anel (criar): {e}")


@anel.command(name="punir", description="⚔️ Punir um usuário — remove todo o dinheiro e itens (Anel Supremo somente).")
async def anel_punir(interaction: discord.Interaction, usuario: discord.Member):
    user_data = get_user_data(interaction.user.id)

    # Verifica se o usuário possui o anel
    if "anel_supremo" not in user_data.get("inventario", {}):
        await interaction.response.send_message(f"{EMOJIS['erro']} Você não possui o Anel Supremo!", ephemeral=True)
        return

    # Checa cooldown diário (um uso por subcomando)
    hoje = datetime.now().date().isoformat()
    if user_data.get("anel_ultimo_uso_punir") == hoje:
        await interaction.response.send_message(f"{EMOJIS['alerta']} Você já usou /anel punir hoje. Tente novamente amanhã.", ephemeral=True)
        return

    alvo_data = get_user_data(usuario.id)

    # Remove dinheiro e itens do alvo
    alvo_data["carteira"] = 0
    alvo_data["banco"] = 0
    alvo_data["inventario"] = {}
    alvo_data["apps"] = []
    alvo_data["celular"] = False
    save_data(data)

    user_data["anel_ultimo_uso_punir"] = hoje
    save_data(data)

    embed = discord.Embed(
        title=f"{EMOJIS['caveira']} Castigo Cósmico!",
        description=(f"⚡ O Anel Supremo libera uma onda de energia divina... {usuario.mention} foi reduzido a pó cósmico.\n\n"
                     "Todos os seus pertences e riquezas desapareceram instantaneamente."),
        color=discord.Color.dark_red(),
        timestamp=datetime.now()
    )
    embed.set_author(name=f"{interaction.user.display_name} — Anel Supremo", icon_url=interaction.user.display_avatar.url)
    embed.add_field(name="Alvo", value=f"{usuario.mention}", inline=True)
    embed.add_field(name="Executor", value=f"{interaction.user.mention}", inline=True)
    embed.set_footer(text="Punição do Anel")
    await interaction.response.send_message(embed=embed)

    # Log em canal de moderação (se configurado)
    try:
        log_channel = bot.get_channel(1398712093238235237)
        if not log_channel:
            try:
                log_channel = await bot.fetch_channel(1398712093238235237)
            except Exception:
                log_channel = None

        if log_channel:
            log_embed = discord.Embed(
                title="Anel Supremo — Punir",
                description=f"{interaction.user.mention} usou `/anel punir` em {usuario.mention}",
                color=discord.Color.dark_red(),
                timestamp=datetime.now()
            )
            log_embed.add_field(name="Executor", value=interaction.user.mention, inline=True)
            log_embed.add_field(name="Alvo", value=usuario.mention, inline=True)
            log_embed.add_field(name="Servidor", value=interaction.guild.name if interaction.guild else "Direto/DM", inline=False)
            await log_channel.send(embed=log_embed)
    except Exception as e:
        print(f"Erro ao enviar log do Anel (punir): {e}")


# adiciona o group ao tree
bot.tree.add_command(anel)

@bot.tree.command(name="transferir", description="💸 Transfira dinheiro para outro usuário")
async def transferir(interaction: discord.Interaction, usuario: discord.Member, quantia: int):
    user_data = get_user_data(interaction.user.id)
    destinatario_data = get_user_data(usuario.id)
    
    if usuario.id == interaction.user.id:
        await interaction.response.send_message(f"{EMOJIS['erro']} Você não pode transferir para si mesmo!", ephemeral=True)
        return
    
    if quantia <= 0:
        await interaction.response.send_message(f"{EMOJIS['erro']} Quantia inválida!", ephemeral=True)
        return
    
    if user_data["carteira"] < quantia:
        await interaction.response.send_message(f"{EMOJIS['erro']} Saldo insuficiente na carteira!", ephemeral=True)
        return
    
    taxa = int(quantia * 0.05)
    quantia_final = quantia - taxa
    
    user_data["carteira"] -= quantia
    destinatario_data["carteira"] += quantia_final
    save_data(data)
    
    embed = discord.Embed(
        title=f"{EMOJIS['sucesso']} Transferência Realizada",
        description=f"Você transferiu **R$ {quantia:,}** para {usuario.display_name}",
        color=discord.Color.green()
    )
    embed.add_field(name="Valor Enviado", value=f"R$ {quantia_final:,}", inline=True)
    embed.add_field(name="Taxa Bancária (5%)", value=f"R$ {taxa:,}", inline=True)
    embed.add_field(name="Seu Saldo", value=f"R$ {user_data['carteira']:,}", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="investir", description="📈 Invista seu dinheiro e arrisque multiplicar")
async def investir(interaction: discord.Interaction, quantia: int):
    user_data = get_user_data(interaction.user.id)
    
    if quantia <= 0:
        await interaction.response.send_message(f"{EMOJIS['erro']} Quantia inválida!", ephemeral=True)
        return
    
    if user_data["carteira"] < quantia:
        await interaction.response.send_message(f"{EMOJIS['erro']} Você não tem esse dinheiro!", ephemeral=True)
        return
    
    if quantia < 500:
        await interaction.response.send_message(f"{EMOJIS['erro']} Investimento mínimo: R$ 500", ephemeral=True)
        return
    
    resultado = random.random()
    
    if resultado < 0.40:
        multiplicador = random.uniform(1.5, 2.5)
        ganho = int(quantia * multiplicador)
        lucro = ganho - quantia
        user_data["carteira"] += lucro
        
        embed = discord.Embed(
            title=f"{EMOJIS['foguete']} Investimento Bem-Sucedido!",
            description=f"Suas ações valorizaram **{multiplicador:.1f}x**!",
            color=discord.Color.green()
        )
        embed.add_field(name="Investimento", value=f"R$ {quantia:,}", inline=True)
        embed.add_field(name="Retorno", value=f"R$ {ganho:,}", inline=True)
        embed.add_field(name="Lucro", value=f"R$ {lucro:,}", inline=True)
        
    else:
        perda_percentual = random.uniform(0.3, 0.7)
        perda = int(quantia * perda_percentual)
        user_data["carteira"] -= quantia
        user_data["carteira"] += (quantia - perda)
        
        embed = discord.Embed(
            title=f"{EMOJIS['alerta']} Mercado em Baixa",
            description=f"Suas ações desvalorizaram {int(perda_percentual * 100)}%",
            color=discord.Color.red()
        )
        embed.add_field(name="Investimento", value=f"R$ {quantia:,}", inline=True)
        embed.add_field(name="Perda", value=f"R$ {perda:,}", inline=True)
        embed.add_field(name="Recuperado", value=f"R$ {quantia - perda:,}", inline=True)
    
    save_data(data)
    embed.set_footer(text="⚠️ Investir envolve riscos!")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="apostar", description="🎰 Aposte no cara ou coroa")
async def apostar(interaction: discord.Interaction, quantia: int, escolha: str):
    user_data = get_user_data(interaction.user.id)
    escolha = escolha.lower()
    
    if escolha not in ["cara", "coroa"]:
        await interaction.response.send_message(f"{EMOJIS['erro']} Escolha 'cara' ou 'coroa'!", ephemeral=True)
        return
    
    if quantia <= 0:
        await interaction.response.send_message(f"{EMOJIS['erro']} Quantia inválida!", ephemeral=True)
        return
    
    if user_data["carteira"] < quantia:
        await interaction.response.send_message(f"{EMOJIS['erro']} Saldo insuficiente!", ephemeral=True)
        return
    
    resultado = random.choice(["cara", "coroa"])
    
    if escolha == resultado:
        ganho = quantia * 2
        user_data["carteira"] += quantia
        
        embed = discord.Embed(
            title=f"{EMOJIS['sucesso']} Você Ganhou!",
            description=f"🪙 A moeda caiu em **{resultado}**!\n\nVocê ganhou **R$ {ganho:,}**!",
            color=discord.Color.gold()
        )
    else:
        user_data["carteira"] -= quantia
        
        embed = discord.Embed(
            title=f"{EMOJIS['erro']} Você Perdeu!",
            description=f"🪙 A moeda caiu em **{resultado}**.\n\nVocê perdeu **R$ {quantia:,}**.",
            color=discord.Color.red()
        )
    
    save_data(data)
    embed.set_footer(text=f"Saldo atual: R$ {user_data['carteira']:,}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="crime", description="🔫 Cometa um crime arriscado por dinheiro")
async def crime(interaction: discord.Interaction):
    user_data = get_user_data(interaction.user.id)
    
    crimes = [
        {"nome": "Hackear caixa eletrônico", "min": 2000, "max": 5000, "chance": 0.3},
        {"nome": "Assaltar joalheria", "min": 3000, "max": 8000, "chance": 0.25},
        {"nome": "Roubar banco", "min": 5000, "max": 15000, "chance": 0.2},
        {"nome": "Contrabandear mercadorias", "min": 1500, "max": 4000, "chance": 0.4},
        {"nome": "Fraudar sistema", "min": 4000, "max": 10000, "chance": 0.25}
    ]
    
    crime_escolhido = random.choice(crimes)
    
    chance_sucesso = crime_escolhido["chance"]
    if "arma_plasma" in user_data["inventario"]:
        chance_sucesso += 0.30
    
    sucesso = random.random() < chance_sucesso
    
    if sucesso:
        ganho = random.randint(crime_escolhido["min"], crime_escolhido["max"])
        user_data["carteira"] += ganho
        user_data["reputacao"] -= 15
        user_data["xp"] += 30
        
        embed = discord.Embed(
            title=f"{EMOJIS['roubou']} Crime Perfeito!",
            description=f"Você conseguiu **{crime_escolhido['nome']}**!\n\n💰 Ganho: **R$ {ganho:,}**\n⚠️ Reputação: **-15**",
            color=discord.Color.dark_green()
        )
    else:
        if "passaporte_falso" in user_data["inventario"]:
            multa = random.randint(300, 1000)
            embed_desc = f"Sua tentativa de **{crime_escolhido['nome']}** falhou!\n\n🚔 Multa reduzida: **R$ {multa:,}** (Passaporte Falso usado)\n⚠️ Reputação: **-15**"
            user_data["reputacao"] -= 15
        else:
            multa = random.randint(1000, 3000)
            embed_desc = f"Sua tentativa de **{crime_escolhido['nome']}** falhou!\n\n🚔 Multa: **R$ {multa:,}**\n⚠️ Reputação: **-25**"
            user_data["reputacao"] -= 25
            
        user_data["carteira"] -= min(multa, user_data["carteira"])
        
        embed = discord.Embed(
            title=f"{EMOJIS['alerta']} Você foi Preso!",
            description=embed_desc,
            color=discord.Color.dark_red()
        )
    
    save_data(data)
    embed.set_footer(text="🔥 Crimes são muito arriscados!")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ranking", description="🏆 Veja os usuários mais ricos do servidor")
async def ranking(interaction: discord.Interaction):
    usuarios_ricos = []
    
    for user_id, user_data in data.items():
        try:
            membro = await interaction.guild.fetch_member(int(user_id))
            total = user_data["carteira"] + user_data["banco"]
            tem_anel = "anel_supremo" in user_data["inventario"]
            usuarios_ricos.append((membro.display_name, total, tem_anel))
        except:
            continue
    
    usuarios_ricos.sort(key=lambda x: x[1], reverse=True)
    top10 = usuarios_ricos[:10]
    
    embed = discord.Embed(
        title=f"{EMOJIS['coroa']} Ranking de Patrimônio",
        description="Os mais ricos do servidor!\n",
        color=discord.Color.gold()
    )
    
    medalhas = ["🥇", "🥈", "🥉"]
    for i, (nome, total, tem_anel) in enumerate(top10):
        medalha = medalhas[i] if i < 3 else f"{i+1}º"
        anel_icon = " 💍" if tem_anel else ""
        embed.add_field(
            name=f"{medalha} {nome}{anel_icon}",
            value=f"R$ {total:,}",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="loja_vip", description="🌟 Veja e compre planos VIP do servidor")
async def loja_vip(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🌟 Loja VIP — Astral Roleplay",
        description="Apoie o servidor e desbloqueie benefícios exclusivos no jogo e no Discord!\n\n**Use o menu abaixo para comprar:**",
        color=discord.Color.purple()
    )
    
    for vip_id, vip_info in VIPS.items():
        beneficios_resumo = "\n".join([f"• {b}" for b in vip_info["beneficios"][:3]])
        
        embed.add_field(
            name=f"{vip_info['emoji']} {vip_info['nome']}",
            value=f"**R$ {vip_info['preco']:,}**\n{beneficios_resumo}",
            inline=True
        )
    
    embed.set_footer(text="💡 O dinheiro do bot será usado para a compra!")
    
    view = VIPPainelView(interaction.user.id)
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="vip", description="🌟 Veja informações sobre seu VIP")
async def vip(interaction: discord.Interaction, usuario: discord.Member = None):
    usuario = usuario or interaction.user
    user_data = get_user_data(usuario.id)
    
    embed = discord.Embed(
        title=f"🌟 Status VIP de {usuario.display_name}",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=usuario.display_avatar.url)
    
    if user_data.get("vip"):
        vip_info = VIPS.get(user_data["vip"])
        if vip_info:
            embed.color = vip_info["cor"]
            embed.description = f"**Plano Ativo:** {vip_info['emoji']} {vip_info['nome']}"
            
            beneficios_text = "\n".join([f"✅ {b}" for b in vip_info["beneficios"]])
            embed.add_field(name="🎁 Benefícios", value=beneficios_text, inline=False)
            embed.add_field(name="💰 Valor do Plano", value=f"R$ {vip_info['preco']:,}", inline=True)
            embed.add_field(name="🎮 Dinheiro no Jogo", value=f"R$ {vip_info['dinheiro_jogo']:,}", inline=True)
        else:
            embed.description = "❌ Você não possui VIP ativo"
            embed.add_field(name="💡 Como Adquirir?", value="Use `/loja_vip` para comprar um plano VIP!", inline=False)
    else:
        embed.description = "❌ Você não possui VIP ativo"
        embed.add_field(name="💡 Como Adquirir?", value="Use `/loja_vip` para comprar um plano VIP!", inline=False)
        embed.add_field(name="🌟 Benefícios VIP", value="Vantagens exclusivas no jogo e Discord\nDinheiro instantâneo no servidor\nCargos e áreas VIP", inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ajuda", description="❓ Veja todos os comandos disponíveis")
async def ajuda(interaction: discord.Interaction):
    embed = discord.Embed(
        title=f"{EMOJIS['diamante']} Central de Ajuda",
        description="Bem-vindo ao sistema de economia mais completo!\n",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name=f"{EMOJIS['dinheiro']} Comandos Básicos",
        value="`/saldo` - Veja seu saldo\n`/perfil` - Perfil completo\n`/daily` - Auxílio diário\n`/inventario` - Seus itens\n`/ranking` - Top usuários\n`/vip` - Ver seu status VIP",
        inline=False
    )
    
    embed.add_field(
        name=f"{EMOJIS['trabalho']} Trabalho",
        value="`/empregos` - Ver e candidatar\n`/trabalhar` - Trabalhar",
        inline=False
    )
    
    embed.add_field(
        name=f"{EMOJIS['celular']} Shopping",
        value="`/loja` - Ver e comprar itens\n`/celular` - Smartphone completo\n`/transferir` - Enviar dinheiro\n`/loja_vip` - 🌟 **Comprar VIP**",
        inline=False
    )
    
    embed.add_field(
        name=f"🎰 Jogos & Riscos",
        value="`/apostar` - Cara ou coroa\n`/investir` - Bolsa de valores\n`/roubar` - Roubar alguém\n`/crime` - Cometer crimes",
        inline=False
    )
    
    embed.set_footer(text="💡 Explore os menus interativos!")
    await interaction.response.send_message(embed=embed)

# ============ COMANDOS ADMIN ============

@bot.tree.command(name="admin_dar_vip", description="👑 [ADMIN] Dar VIP para um usuário")
@app_commands.checks.has_permissions(administrator=True)
async def admin_dar_vip(interaction: discord.Interaction, usuario: discord.Member, vip: str):
    vip = vip.lower()
    
    if vip not in VIPS:
        vips_disponiveis = ", ".join(VIPS.keys())
        await interaction.response.send_message(
            f"{EMOJIS['erro']} VIP inválido! Disponíveis: {vips_disponiveis}",
            ephemeral=True
        )
        return
    
    user_data = get_user_data(usuario.id)
    vip_info = VIPS[vip]
    
    user_data["vip"] = vip
    
    cargo_adicionado = False
    if vip_info["cargo_id"]:
        try:
            cargo = interaction.guild.get_role(vip_info["cargo_id"])
            if cargo:
                await usuario.add_roles(cargo)
                cargo_adicionado = True
        except Exception as e:
            print(f"Erro ao adicionar cargo VIP: {e}")
    
    save_data(data)
    
    embed = discord.Embed(
        title=f"{EMOJIS['sucesso']} VIP Concedido!",
        description=f"{vip_info['emoji']} **{vip_info['nome']}** foi dado para {usuario.mention}",
        color=vip_info["cor"]
    )
    
    beneficios_text = "\n".join([f"✅ {b}" for b in vip_info["beneficios"]])
    embed.add_field(name="Benefícios", value=beneficios_text, inline=False)
    embed.add_field(name="💰 Dinheiro no Jogo", value=f"R$ {vip_info['dinheiro_jogo']:,}", inline=True)
    
    if cargo_adicionado:
        embed.add_field(name="👥 Cargo", value="✅ Adicionado", inline=True)
    else:
        embed.add_field(name="👥 Cargo", value="⚠️ Não configurado", inline=True)
    
    embed.set_footer(text="🎮 O jogador deve entrar no servidor para receber os benefícios!")
    
    await interaction.response.send_message(embed=embed)
    
    try:
        dm_embed = discord.Embed(
            title=f"🎉 Você recebeu VIP!",
            description=f"Um administrador te concedeu o **{vip_info['emoji']} {vip_info['nome']}**!",
            color=vip_info["cor"]
        )
        dm_embed.add_field(name="Benefícios", value=beneficios_text, inline=False)
        dm_embed.set_footer(text="Entre no servidor para aproveitar seus benefícios!")
        await usuario.send(embed=dm_embed)
    except:
        pass

@bot.tree.command(name="admin_remover_vip", description="👑 [ADMIN] Remover VIP de um usuário")
@app_commands.checks.has_permissions(administrator=True)
async def admin_remover_vip(interaction: discord.Interaction, usuario: discord.Member):
    user_data = get_user_data(usuario.id)
    
    if not user_data.get("vip"):
        await interaction.response.send_message(
            f"{EMOJIS['erro']} {usuario.display_name} não possui VIP!",
            ephemeral=True
        )
        return
    
    vip_removido = user_data["vip"]
    vip_info = VIPS.get(vip_removido)
    
    if vip_info and vip_info["cargo_id"]:
        try:
            cargo = interaction.guild.get_role(vip_info["cargo_id"])
            if cargo and cargo in usuario.roles:
                await usuario.remove_roles(cargo)
        except Exception as e:
            print(f"Erro ao remover cargo VIP: {e}")
    
    user_data["vip"] = None
    user_data["vip_expira"] = None
    save_data(data)
    
    embed = discord.Embed(
        title=f"{EMOJIS['sucesso']} VIP Removido",
        description=f"O VIP de {usuario.mention} foi removido.",
        color=discord.Color.red()
    )
    
    if vip_info:
        embed.add_field(name="VIP Removido", value=f"{vip_info['emoji']} {vip_info['nome']}", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="admin_listar_vips", description="👑 [ADMIN] Ver todos os usuários com VIP")
@app_commands.checks.has_permissions(administrator=True)
async def admin_listar_vips(interaction: discord.Interaction):
    usuarios_vip = []
    
    for user_id, user_data in data.items():
        if user_data.get("vip"):
            try:
                membro = await interaction.guild.fetch_member(int(user_id))
                vip_info = VIPS.get(user_data["vip"])
                if vip_info:
                    usuarios_vip.append((membro.display_name, vip_info["nome"], vip_info["emoji"]))
            except:
                continue
    
    embed = discord.Embed(
        title="🌟 Lista de VIPs do Servidor",
        color=discord.Color.purple()
    )
    
    if not usuarios_vip:
        embed.description = "Nenhum usuário possui VIP no momento."
    else:
        vip_text = ""
        for nome, vip_nome, emoji in usuarios_vip:
            vip_text += f"{emoji} **{nome}** — {vip_nome}\n"
        embed.description = vip_text
    
    embed.set_footer(text=f"Total de VIPs: {len(usuarios_vip)}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="admin_configurar_cargo_vip", description="👑 [ADMIN] Configurar ID do cargo VIP")
@app_commands.checks.has_permissions(administrator=True)
async def admin_configurar_cargo_vip(interaction: discord.Interaction, vip: str, cargo_id: str):
    vip = vip.lower()
    
    if vip not in VIPS:
        vips_disponiveis = ", ".join(VIPS.keys())
        await interaction.response.send_message(
            f"{EMOJIS['erro']} VIP inválido! Disponíveis: {vips_disponiveis}",
            ephemeral=True
        )
        return
    
    try:
        cargo_id_int = int(cargo_id)
        cargo = interaction.guild.get_role(cargo_id_int)
        
        if not cargo:
            await interaction.response.send_message(
                f"{EMOJIS['erro']} Cargo não encontrado! Verifique o ID.",
                ephemeral=True
            )
            return
        
        VIPS[vip]["cargo_id"] = cargo_id_int
        
        embed = discord.Embed(
            title=f"{EMOJIS['sucesso']} Cargo Configurado!",
            description=f"O cargo {cargo.mention} foi vinculado ao **{VIPS[vip]['nome']}**",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"ID do cargo: {cargo_id_int}")
        
        await interaction.response.send_message(embed=embed)
        
    except ValueError:
        await interaction.response.send_message(
            f"{EMOJIS['erro']} ID inválido! Use apenas números.",
            ephemeral=True
        )

@bot.tree.command(name="admin_painel_vip", description="👑 [ADMIN] Criar painel público de VIPs")
@app_commands.checks.has_permissions(administrator=True)
async def admin_painel_vip(interaction: discord.Interaction, canal: discord.TextChannel = None):
    canal = canal or interaction.channel
    
    embed = discord.Embed(
        title="🌟 Planos VIP — Astral Roleplay",
        description="**Apoie o servidor e desbloqueie benefícios exclusivos no jogo e no Discord!**\n\nUse seus créditos do bot de economia para adquirir VIP!\nUse `/loja_vip` para comprar.\n",
        color=discord.Color.from_rgb(138, 43, 226)
    )
    
    embed.add_field(
        name="⭐ VIP Alpha — R$3.000",
        value="• Acesso à área VIP\n• Fila prioritária em tickets\n• **R$100.000,00** no jogo",
        inline=False
    )
    
    embed.add_field(
        name="💎 VIP Beta — R$10.000",
        value="• Tudo do Alpha\n• **R$250.000,00** no jogo\n• Cargo diferenciado no Discord",
        inline=False
    )
    
    embed.add_field(
        name="👑 VIP Ômega — R$18.000",
        value="• Tudo do Beta\n• **R$300.000,00** no jogo\n• Salário VIP",
        inline=False
    )
    
    embed.add_field(
        name="💠 VIP Diamond — R$30.000",
        value="• Tudo do Ômega\n• **R$750.000,00** no jogo\n• Loja VIP no jogo\n• Tag VIP DIAMOND\n• 1 veículo exclusivo",
        inline=False
    )
    
    embed.add_field(
        name="💫 VIP Diamond 2.0 — R$50.000",
        value="• Tudo do Diamond\n• 2 veículos únicos\n• **R$1.000.000,00** no jogo\n• Acesso antecipado a updates\n• Cores especiais no chat",
        inline=False
    )
    
    embed.set_footer(text="💰 Use /loja_vip para comprar | 🎮 Entre no servidor após a compra para receber os benefícios")
    embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
    
    await canal.send(embed=embed)
    
    confirmacao = discord.Embed(
        title=f"{EMOJIS['sucesso']} Painel Criado!",
        description=f"O painel VIP foi enviado para {canal.mention}",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=confirmacao, ephemeral=True)


@bot.tree.command(name="admin_sorteio", description="👑 [ADMIN] Realizar um sorteio — escolhe uma pessoa (não-bot) do servidor")
@app_commands.checks.has_permissions(administrator=True)
async def admin_sorteio(interaction: discord.Interaction, nome: str = None):
    """Escolhe aleatoriamente um membro humano do servidor e anuncia o sorteio.
    Parâmetros:
    - nome (opcional): mostra esse nome na mensagem pública (para o admin 'roubar um pouquinho').
    Observação: o vencedor real é escolhido aleatoriamente; se você fornecer `nome`, o anúncio público mostrará o texto fornecido,
    enquanto o executor do comando receberá uma confirmação ephemera com o vencedor real.
    """
    if not interaction.guild:
        await interaction.response.send_message(f"{EMOJIS['erro']} Este comando só pode ser usado em servidores.", ephemeral=True)
        return

    # Recolhe membros humanos (não bots).
    members = [m for m in interaction.guild.members if not m.bot]

    # Se cache não contiver membros (grandes servidores), tente fetch
    if not members:
        try:
            members = [m async for m in interaction.guild.fetch_members(limit=None) if not m.bot]
        except Exception:
            await interaction.response.send_message(f"{EMOJIS['erro']} Não foi possível obter a lista de membros. Tente novamente mais tarde.", ephemeral=True)
            return

    if not members:
        await interaction.response.send_message(f"{EMOJIS['erro']} Nenhum membro humano encontrado para sortear.", ephemeral=True)
        return

    vencedor = random.choice(members)

    # Mensagem pública: se nome fornecido, mostramos esse nome (sem mencionar o vencedor);
    # o executor recebe confirmação ephemera com o vencedor real para controle.
    if nome:
        public_embed = discord.Embed(
            title="🎉 Sorteio Realizado!",
            description=f"Parabéns, **{nome}** — você foi sorteado!",
            color=discord.Color.purple(),
            timestamp=datetime.now()
        )
        public_embed.add_field(name="Nota", value="Vencedor real notificado ao administrador.", inline=False)
        public_embed.set_footer(text=f"Sorteio por {interaction.user.display_name}")
        await interaction.response.send_message(embed=public_embed)

        # enviar confirmação ephemera para o admin com o vencedor real (embed)
        try:
            confirm_embed = discord.Embed(
                title="🏆 Vencedor Real",
                description=f"{vencedor.mention}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            confirm_embed.add_field(name="Nome exibido publicamente", value=nome, inline=False)
            await interaction.followup.send(embed=confirm_embed, ephemeral=True)
        except Exception:
            # fallback: resposta ephemera direta
            await interaction.response.send_message(f"(Confirmação) Vencedor real: {vencedor.mention}", ephemeral=True)
    else:
        public_embed = discord.Embed(
            title="🎉 Sorteio Realizado!",
            description=f"Parabéns {vencedor.mention} — você foi sorteado!",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        public_embed.set_footer(text=f"Sorteio por {interaction.user.display_name}")
        # se houver ícone do servidor, coloca como thumbnail
        try:
            if interaction.guild and interaction.guild.icon:
                public_embed.set_thumbnail(url=interaction.guild.icon.url)
        except Exception:
            pass
        await interaction.response.send_message(embed=public_embed)

    # Log no console (e opcionalmente poderia enviar para um canal de moderação)
    print(f"[SORTEIO] Executor: {interaction.user} | Vencedor: {vencedor} | exibido_nome: {nome or vencedor.display_name}")

@bot.tree.command(name="admin_add", description="👑 [ADMIN] Adicionar dinheiro a um usuário")
@app_commands.checks.has_permissions(administrator=True)
async def admin_add(interaction: discord.Interaction, usuario: discord.Member, quantia: int):
    user_data = get_user_data(usuario.id)
    user_data["carteira"] += quantia
    save_data(data)
    
    embed = discord.Embed(
        title=f"{EMOJIS['sucesso']} Dinheiro Adicionado",
        description=f"**R$ {quantia:,}** foram adicionados à carteira de {usuario.display_name}",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="admin_remove", description="👑 [ADMIN] Remover dinheiro de um usuário")
@app_commands.checks.has_permissions(administrator=True)
async def admin_remove(interaction: discord.Interaction, usuario: discord.Member, quantia: int):
    user_data = get_user_data(usuario.id)
    user_data["carteira"] = max(0, user_data["carteira"] - quantia)
    save_data(data)
    
    embed = discord.Embed(
        title=f"{EMOJIS['sucesso']} Dinheiro Removido",
        description=f"**R$ {quantia:,}** foram removidos da carteira de {usuario.display_name}",
        color=discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="admin_dar_item", description="👑 [ADMIN] Dar um item para um usuário")
@app_commands.checks.has_permissions(administrator=True)
async def admin_dar_item(interaction: discord.Interaction, usuario: discord.Member, item: str):
    user_data = get_user_data(usuario.id)
    item = item.lower().replace(" ", "_")
    
    item_encontrado = None
    item_info = None
    
    if item in LOJA:
        item_encontrado = item
        item_info = LOJA[item]
    elif item in MERCADO_NEGRO:
        item_encontrado = item
        item_info = MERCADO_NEGRO[item]
    
    if not item_encontrado:
        await interaction.response.send_message(f"{EMOJIS['erro']} Item não encontrado!", ephemeral=True)
        return
    
    if item in user_data["inventario"]:
        await interaction.response.send_message(f"{EMOJIS['erro']} {usuario.display_name} já possui este item!", ephemeral=True)
        return
    
    user_data["inventario"][item] = 1
    save_data(data)
    
    embed = discord.Embed(
        title=f"{EMOJIS['presente']} Item Entregue!",
        description=f"{item_info['emoji']} **{item.replace('_', ' ').title()}** foi dado para {usuario.display_name}",
        color=discord.Color.gold()
    )
    
    if item == "anel_supremo":
        embed.description += f"\n\n💍 **O PODER SUPREMO FOI CONCEDIDO!** 💍"
        embed.color = discord.Color.purple()
    
    await interaction.response.send_message(embed=embed)

# ============ CONFIGURAÇÃO INICIAL ============

DATA_FILE = "economy_data.json"

# ============ SISTEMA VIP ============

VIPS = {
    "alpha": {
        "nome": "VIP Alpha",
        "preco": 3000,
        "emoji": "⭐",
        "cor": discord.Color.blue(),
        "beneficios": [
            "Acesso à área VIP",
            "Fila prioritária em tickets",
            "R$100.000,00 no jogo"
        ],
        "dinheiro_jogo": 100000,
        "cargo_id": None
    },
    "beta": {
        "nome": "VIP Beta",
        "preco": 10000,
        "emoji": "💎",
        "cor": discord.Color.purple(),
        "beneficios": [
            "Tudo do Alpha",
            "R$250.000,00 no jogo",
            "Cargo diferenciado no Discord"
        ],
        "dinheiro_jogo": 250000,
        "cargo_id": None
    },
    "omega": {
        "nome": "VIP Ômega",
        "preco": 18000,
        "emoji": "👑",
        "cor": discord.Color.gold(),
        "beneficios": [
            "Tudo do Beta",
            "R$300.000,00 no jogo",
            "Salário VIP"
        ],
        "dinheiro_jogo": 300000,
        "cargo_id": None
    },
    "diamond": {
        "nome": "VIP Diamond",
        "preco": 30000,
        "emoji": "💠",
        "cor": discord.Color.from_rgb(0, 255, 255),
        "beneficios": [
            "Tudo do Ômega",
            "R$750.000,00 no jogo",
            "Loja VIP no jogo",
            "Tag VIP DIAMOND",
            "1 veículo exclusivo"
        ],
        "dinheiro_jogo": 750000,
        "cargo_id": None
    },
    "diamond2": {
        "nome": "VIP Diamond 2.0",
        "preco": 50000,
        "emoji": "💫",
        "cor": discord.Color.from_rgb(255, 0, 255),
        "beneficios": [
            "Tudo do Diamond",
            "2 veículos únicos",
            "R$1.000.000,00 no jogo",
            "Acesso antecipado a updates",
            "Cores especiais no chat"
        ],
        "dinheiro_jogo": 1000000,
        "cargo_id": None
    }
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data_to_save):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, indent=4, ensure_ascii=False)

data = load_data()

def get_user_data(user_id):
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {
            "carteira": 1000,
            "banco": 0,
            "inventario": {},
            "trabalho": None,
            "ultimo_trabalho": None,
            "ultimo_daily": None,
            "ultimo_roubo": None,
            "celular": False,
            "apps": [],
            "nivel": 1,
            "xp": 0,
            "reputacao": 0,
            "vip": None,
            "vip_expira": None,
            # Anel Supremo usage tracking (separado por subcomando)
            "anel_ultimo_uso_criar": None,
            "anel_ultimo_uso_punir": None
        }
        save_data(data)
    return data[user_id]

# ============ EMOJIS E DADOS ============

EMOJIS = {
    "dinheiro": "💰",
    "banco": "🏦",
    "carteira": "👛",
    "trabalho": "💼",
    "celular": "📱",
    "roubou": "🎭",
    "presente": "🎁",
    "estrela": "⭐",
    "foguete": "🚀",
    "coroa": "👑",
    "diamante": "💎",
    "alerta": "⚠️",
    "sucesso": "✅",
    "erro": "❌",
    "relogio": "⏰",
    "grafico": "📊",
    "caveira": "💀"
}

TRABALHOS = {
    "entregador": {"salario": 500, "tempo": 3600, "nivel_min": 1, "emoji": "🛵"},
    "caixa": {"salario": 750, "tempo": 3600, "nivel_min": 2, "emoji": "🧾"},
    "programador": {"salario": 1500, "tempo": 7200, "nivel_min": 5, "emoji": "💻"},
    "medico": {"salario": 3000, "tempo": 10800, "nivel_min": 10, "emoji": "⚕️"},
    "empresario": {"salario": 5000, "tempo": 14400, "nivel_min": 15, "emoji": "🏢"}
}

LOJA = {
    "celular": {"preco": 2000, "emoji": "📱", "descricao": "Desbloqueie apps e funcionalidades!"},
    "pc_gamer": {"preco": 5000, "emoji": "🖥️", "descricao": "Aumente seus ganhos em 20%"},
    "carro": {"preco": 15000, "emoji": "🚗", "descricao": "Reduza tempo de trabalho"},
    "mansao": {"preco": 50000, "emoji": "🏰", "descricao": "Status máximo de luxo!"},
    "iate": {"preco": 100000, "emoji": "🛥️", "descricao": "O sonho de qualquer milionário"},
    "anel_supremo": {"preco": 999999999, "emoji": "💍", "descricao": "⚠️ ITEM SECRETO - Poder absoluto!", "secreto": True}
}

APPS = {
    "banco_digital": {"preco": 500, "emoji": "💳", "beneficio": "Transferências instantâneas"},
    "bolsa_valores": {"preco": 2000, "emoji": "📈", "beneficio": "Invista e multiplique seu dinheiro"},
    "delivery": {"preco": 800, "emoji": "🍔", "beneficio": "Ganhe dinheiro fazendo entregas"},
    "uber": {"preco": 1000, "emoji": "🚕", "beneficio": "Trabalhe como motorista"}
}

MERCADO_NEGRO = {
    "arma_plasma": {"preco": 25000, "emoji": "🔫", "descricao": "Aumenta chance de crimes em 30%"},
    "diamante_sangue": {"preco": 50000, "emoji": "💎", "descricao": "Vale muito no mercado negro"},
    "passaporte_falso": {"preco": 15000, "emoji": "📘", "descricao": "Evite ser preso"},
    "chip_hacker": {"preco": 30000, "emoji": "🔌", "descricao": "Hackeie sistemas com sucesso"}
}

# ============ VIEWS E SELECTS - ECONOMIA ============

class LojaView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.add_item(LojaSelect(user_id))
    
    @discord.ui.button(label="Fechar", emoji="❌", style=discord.ButtonStyle.danger, row=1)
    async def fechar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['erro']} Esta não é sua loja!", ephemeral=True)
            return
        await interaction.message.delete()

class LojaSelect(discord.ui.Select):
    def __init__(self, user_id):
        self.user_id = user_id
        options = []
        
        for item_id, item_info in LOJA.items():
            if item_info.get("secreto"):
                continue
            options.append(
                discord.SelectOption(
                    label=item_id.replace('_', ' ').title(),
                    description=f"R$ {item_info['preco']:,} - {item_info['descricao'][:50]}",
                    emoji=item_info['emoji'],
                    value=item_id
                )
            )
        
        super().__init__(placeholder="Escolha um item para comprar...", options=options, row=0)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['erro']} Esta não é sua loja!", ephemeral=True)
            return
        
        item = self.values[0]
        user_data = get_user_data(self.user_id)
        
        if item in user_data["inventario"]:
            await interaction.response.send_message(f"{EMOJIS['erro']} Você já possui este item!", ephemeral=True)
            return
        
        preco = LOJA[item]["preco"]
        if user_data["carteira"] < preco:
            await interaction.response.send_message(
                f"{EMOJIS['erro']} Saldo insuficiente! Faltam R$ {preco - user_data['carteira']:,}",
                ephemeral=True
            )
            return
        
        user_data["carteira"] -= preco
        user_data["inventario"][item] = 1
        save_data(data)
        
        embed = discord.Embed(
            title=f"{EMOJIS['sucesso']} Compra Realizada!",
            description=f"Você adquiriu **{item.replace('_', ' ').title()}** {LOJA[item]['emoji']}\n\n{LOJA[item]['descricao']}",
            color=discord.Color.green()
        )
        embed.add_field(name="Saldo Restante", value=f"R$ {user_data['carteira']:,}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class EmpregosView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.add_item(EmpregosSelect(user_id))
    
    @discord.ui.button(label="Fechar", emoji="❌", style=discord.ButtonStyle.danger, row=1)
    async def fechar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['erro']} Este não é seu menu!", ephemeral=True)
            return
        await interaction.message.delete()

class EmpregosSelect(discord.ui.Select):
    def __init__(self, user_id):
        self.user_id = user_id
        user_data = get_user_data(user_id)
        options = []
        
        for emprego_id, emprego_info in TRABALHOS.items():
            disponivel = user_data["nivel"] >= emprego_info["nivel_min"]
            desc = f"R$ {emprego_info['salario']:,}/h - "
            desc += "Disponível" if disponivel else f"Nível {emprego_info['nivel_min']} necessário"
            
            options.append(
                discord.SelectOption(
                    label=emprego_id.title(),
                    description=desc[:100],
                    emoji=emprego_info['emoji'],
                    value=emprego_id
                )
            )
        
        super().__init__(placeholder="Escolha uma profissão...", options=options, row=0)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['erro']} Este não é seu menu!", ephemeral=True)
            return
        
        emprego = self.values[0]
        user_data = get_user_data(self.user_id)
        
        if user_data["nivel"] < TRABALHOS[emprego]["nivel_min"]:
            await interaction.response.send_message(
                f"{EMOJIS['erro']} Você precisa ser nível {TRABALHOS[emprego]['nivel_min']} para este emprego!",
                ephemeral=True
            )
            return
        
        user_data["trabalho"] = emprego
        save_data(data)
        
        embed = discord.Embed(
            title=f"{EMOJIS['sucesso']} Parabéns!",
            description=f"Você foi contratado como **{emprego.title()}**!\n\nComece a trabalhar usando `/trabalhar`",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class CelularView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=180)
        self.user_id = user_id
    
    @discord.ui.button(label="Play Store", emoji="🏪", style=discord.ButtonStyle.primary)
    async def playstore_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['erro']} Este não é seu celular!", ephemeral=True)
            return
        
        user_data = get_user_data(self.user_id)
        embed = discord.Embed(
            title="🏪 Play Store",
            description="Baixe apps úteis para seu celular!\n",
            color=discord.Color.green()
        )
        
        for app, info in APPS.items():
            ja_possui = app in user_data["apps"]
            status = "✅ Instalado" if ja_possui else f"💰 R$ {info['preco']:,}"
            
            embed.add_field(
                name=f"{info['emoji']} {app.replace('_', ' ').title()}",
                value=f"{info['beneficio']}\n**{status}**",
                inline=True
            )
        
        embed.set_footer(text="Use o menu abaixo para instalar apps!")
        view = PlayStoreView(self.user_id)
        await interaction.response.edit_message(embed=embed, view=view)
    
    @discord.ui.button(label="Mercado Negro", emoji="🎭", style=discord.ButtonStyle.danger)
    async def mercado_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['erro']} Este não é seu celular!", ephemeral=True)
            return
        
        user_data = get_user_data(self.user_id)
        embed = discord.Embed(
            title="🎭 Mercado Negro",
            description="⚠️ Itens raros e ilegais... use por sua conta e risco!\n",
            color=discord.Color.dark_red()
        )
        
        for item, info in MERCADO_NEGRO.items():
            ja_possui = item in user_data["inventario"]
            status = "✅ Possui" if ja_possui else f"💰 R$ {info['preco']:,}"
            
            embed.add_field(
                name=f"{info['emoji']} {item.replace('_', ' ').title()}",
                value=f"{info['descricao']}\n**{status}**",
                inline=True
            )
        
        embed.set_footer(text="⚠️ Compras no mercado negro diminuem sua reputação!")
        view = MercadoNegroView(self.user_id)
        await interaction.response.edit_message(embed=embed, view=view)
    
    @discord.ui.button(label="Banco Digital", emoji="💳", style=discord.ButtonStyle.secondary)
    async def banco_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['erro']} Este não é seu celular!", ephemeral=True)
            return
        
        user_data = get_user_data(self.user_id)
        
        if "banco_digital" not in user_data["apps"]:
            await interaction.response.send_message(f"{EMOJIS['erro']} Você precisa do app Banco Digital!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="💳 Banco Digital",
            description="Gerencie suas finanças pelo celular!\n",
            color=discord.Color.blue()
        )
        embed.add_field(name="💰 Carteira", value=f"R$ {user_data['carteira']:,}", inline=True)
        embed.add_field(name="🏦 Banco", value=f"R$ {user_data['banco']:,}", inline=True)
        embed.add_field(name="📊 Total", value=f"R$ {user_data['carteira'] + user_data['banco']:,}", inline=True)
        
        view = BancoView(self.user_id)
        await interaction.response.edit_message(embed=embed, view=view)
    
    @discord.ui.button(label="Meus Apps", emoji="📂", style=discord.ButtonStyle.success)
    async def apps_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['erro']} Este não é seu celular!", ephemeral=True)
            return
        
        user_data = get_user_data(self.user_id)
        embed = discord.Embed(
            title="📂 Meus Aplicativos",
            color=discord.Color.blue()
        )
        
        if not user_data["apps"]:
            embed.description = "Nenhum app instalado. Visite a Play Store!"
        else:
            apps_text = ""
            for app in user_data["apps"]:
                if app in APPS:
                    info = APPS[app]
                    apps_text += f"{info['emoji']} **{app.replace('_', ' ').title()}**\n{info['beneficio']}\n\n"
            embed.description = apps_text
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Fechar", emoji="❌", style=discord.ButtonStyle.danger, row=1)
    async def fechar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['erro']} Este não é seu celular!", ephemeral=True)
            return
        await interaction.message.delete()

class PlayStoreView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.add_item(PlayStoreSelect(user_id))
        
        voltar_btn = discord.ui.Button(label="Voltar", emoji="◀️", style=discord.ButtonStyle.secondary, row=1)
        voltar_btn.callback = self.voltar_callback
        self.add_item(voltar_btn)
    
    async def voltar_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['erro']} Este não é seu celular!", ephemeral=True)
            return
        
        user_data = get_user_data(self.user_id)
        embed = discord.Embed(
            title=f"{EMOJIS['celular']} Meu Smartphone",
            description="📱 Seu hub central para tudo!\n\nEscolha um app abaixo:",
            color=discord.Color.blue()
        )
        embed.add_field(name="📱 Modelo", value="iPhone 15 Pro Max", inline=True)
        embed.add_field(name="📦 Apps Instalados", value=str(len(user_data["apps"])), inline=True)
        embed.add_field(name="🔋 Bateria", value="100%", inline=True)
        
        view = CelularView(self.user_id)
        await interaction.response.edit_message(embed=embed, view=view)

class PlayStoreSelect(discord.ui.Select):
    def __init__(self, user_id):
        self.user_id = user_id
        user_data = get_user_data(user_id)
        options = []
        
        for app_id, app_info in APPS.items():
            ja_possui = app_id in user_data["apps"]
            status = "✅ Instalado" if ja_possui else f"R$ {app_info['preco']:,}"
            
            options.append(
                discord.SelectOption(
                    label=app_id.replace('_', ' ').title(),
                    description=f"{status} - {app_info['beneficio'][:50]}",
                    emoji=app_info['emoji'],
                    value=app_id
                )
            )
        
        super().__init__(placeholder="Escolha um app para instalar...", options=options, row=0)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['erro']} Este não é seu celular!", ephemeral=True)
            return
        
        app_id = self.values[0]
        user_data = get_user_data(self.user_id)
        
        if app_id in user_data["apps"]:
            await interaction.response.send_message(f"{EMOJIS['erro']} App já instalado!", ephemeral=True)
            return
        
        preco = APPS[app_id]["preco"]
        if user_data["carteira"] < preco:
            await interaction.response.send_message(
                f"{EMOJIS['erro']} Saldo insuficiente! Faltam R$ {preco - user_data['carteira']:,}",
                ephemeral=True
            )
            return
        
        user_data["carteira"] -= preco
        user_data["apps"].append(app_id)
        save_data(data)
        
        await interaction.response.send_message(
            f"{EMOJIS['sucesso']} **{app_id.replace('_', ' ').title()}** instalado com sucesso!",
            ephemeral=True
        )

class MercadoNegroView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.add_item(MercadoNegroSelect(user_id))
        
        voltar_btn = discord.ui.Button(label="Voltar", emoji="◀️", style=discord.ButtonStyle.secondary, row=1)
        voltar_btn.callback = self.voltar_callback
        self.add_item(voltar_btn)
    
    async def voltar_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['erro']} Este não é seu celular!", ephemeral=True)
            return
        
        user_data = get_user_data(self.user_id)
        embed = discord.Embed(
            title=f"{EMOJIS['celular']} Meu Smartphone",
            description="📱 Seu hub central para tudo!\n\nEscolha um app abaixo:",
            color=discord.Color.blue()
        )
        embed.add_field(name="📱 Modelo", value="iPhone 15 Pro Max", inline=True)
        embed.add_field(name="📦 Apps Instalados", value=str(len(user_data["apps"])), inline=True)
        embed.add_field(name="🔋 Bateria", value="100%", inline=True)
        
        view = CelularView(self.user_id)
        await interaction.response.edit_message(embed=embed, view=view)

class MercadoNegroSelect(discord.ui.Select):
    def __init__(self, user_id):
        self.user_id = user_id
        user_data = get_user_data(user_id)
        options = []
        
        for item_id, item_info in MERCADO_NEGRO.items():
            ja_possui = item_id in user_data["inventario"]
            status = "✅ Possui" if ja_possui else f"R$ {item_info['preco']:,}"
            
            options.append(
                discord.SelectOption(
                    label=item_id.replace('_', ' ').title(),
                    description=f"{status} - {item_info['descricao'][:50]}",
                    emoji=item_info['emoji'],
                    value=item_id
                )
            )
        
        super().__init__(placeholder="Escolha um item para comprar...", options=options, row=0)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['erro']} Este não é seu celular!", ephemeral=True)
            return
        
        item_id = self.values[0]
        user_data = get_user_data(self.user_id)
        
        if item_id in user_data["inventario"]:
            await interaction.response.send_message(f"{EMOJIS['erro']} Você já possui este item!", ephemeral=True)
            return
        
        preco = MERCADO_NEGRO[item_id]["preco"]
        if user_data["carteira"] < preco:
            await interaction.response.send_message(
                f"{EMOJIS['erro']} Dinheiro insuficiente! Faltam R$ {preco - user_data['carteira']:,}",
                ephemeral=True
            )
            return
        
        user_data["carteira"] -= preco
        user_data["inventario"][item_id] = 1
        user_data["reputacao"] -= 20
        save_data(data)
        
        await interaction.response.send_message(
            f"{EMOJIS['roubou']} **{item_id.replace('_', ' ').title()}** comprado! Sua reputação diminuiu (-20).",
            ephemeral=True
        )

class BancoView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=180)
        self.user_id = user_id
    
    @discord.ui.button(label="Depositar", emoji="⬇️", style=discord.ButtonStyle.success)
    async def depositar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['erro']} Este não é seu celular!", ephemeral=True)
            return
        
        modal = DepositarModal(self.user_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Sacar", emoji="⬆️", style=discord.ButtonStyle.primary)
    async def sacar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['erro']} Este não é seu celular!", ephemeral=True)
            return
        
        modal = SacarModal(self.user_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Voltar", emoji="◀️", style=discord.ButtonStyle.secondary)
    async def voltar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['erro']} Este não é seu celular!", ephemeral=True)
            return
        
        user_data = get_user_data(self.user_id)
        embed = discord.Embed(
            title=f"{EMOJIS['celular']} Meu Smartphone",
            description="📱 Seu hub central para tudo!\n\nEscolha um app abaixo:",
            color=discord.Color.blue()
        )
        embed.add_field(name="📱 Modelo", value="iPhone 15 Pro Max", inline=True)
        embed.add_field(name="📦 Apps Instalados", value=str(len(user_data["apps"])), inline=True)
        embed.add_field(name="🔋 Bateria", value="100%", inline=True)
        
        view = CelularView(self.user_id)
        await interaction.response.edit_message(embed=embed, view=view)

class DepositarModal(discord.ui.Modal, title="Depositar Dinheiro"):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
    
    quantia = discord.ui.TextInput(
        label="Quanto deseja depositar?",
        placeholder="Digite o valor em R$",
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            valor = int(self.quantia.value)
            user_data = get_user_data(self.user_id)
            
            if valor <= 0:
                await interaction.response.send_message(f"{EMOJIS['erro']} Valor inválido!", ephemeral=True)
                return
            
            if user_data["carteira"] < valor:
                await interaction.response.send_message(f"{EMOJIS['erro']} Saldo insuficiente!", ephemeral=True)
                return
            
            user_data["carteira"] -= valor
            user_data["banco"] += valor
            save_data(data)
            
            await interaction.response.send_message(
                f"{EMOJIS['sucesso']} R$ {valor:,} depositados com sucesso!",
                ephemeral=True
            )
        except ValueError:
            await interaction.response.send_message(f"{EMOJIS['erro']} Digite apenas números!", ephemeral=True)

class SacarModal(discord.ui.Modal, title="Sacar Dinheiro"):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
    
    quantia = discord.ui.TextInput(
        label="Quanto deseja sacar?",
        placeholder="Digite o valor em R$",
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            valor = int(self.quantia.value)
            user_data = get_user_data(self.user_id)
            
            if valor <= 0:
                await interaction.response.send_message(f"{EMOJIS['erro']} Valor inválido!", ephemeral=True)
                return
            
            if user_data["banco"] < valor:
                await interaction.response.send_message(f"{EMOJIS['erro']} Saldo insuficiente no banco!", ephemeral=True)
                return
            
            user_data["banco"] -= valor
            user_data["carteira"] += valor
            save_data(data)
            
            await interaction.response.send_message(
                f"{EMOJIS['sucesso']} R$ {valor:,} sacados com sucesso!",
                ephemeral=True
            )
        except ValueError:
            await interaction.response.send_message(f"{EMOJIS['erro']} Digite apenas números!", ephemeral=True)

# ============ VIEWS VIP ============

class VIPPainelView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.add_item(VIPSelect(user_id))
    
    @discord.ui.button(label="Meu VIP", emoji="👤", style=discord.ButtonStyle.secondary, row=1)
    async def meu_vip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['erro']} Este não é seu painel!", ephemeral=True)
            return
        
        user_data = get_user_data(self.user_id)
        embed = discord.Embed(title="👤 Seu Status VIP", color=discord.Color.blue())
        
        if user_data.get("vip"):
            vip_info = VIPS.get(user_data["vip"])
            if vip_info:
                embed.description = f"**Plano Ativo:** {vip_info['emoji']} {vip_info['nome']}"
                embed.color = vip_info["cor"]
                beneficios_text = "\n".join([f"✅ {b}" for b in vip_info["beneficios"]])
                embed.add_field(name="Benefícios", value=beneficios_text, inline=False)
            else:
                embed.description = "❌ Você não possui VIP ativo"
        else:
            embed.description = "❌ Você não possui VIP ativo"
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="Fechar", emoji="❌", style=discord.ButtonStyle.danger, row=1)
    async def fechar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['erro']} Este não é seu painel!", ephemeral=True)
            return
        await interaction.message.delete()

class VIPSelect(discord.ui.Select):
    def __init__(self, user_id):
        self.user_id = user_id
        options = []
        
        for vip_id, vip_info in VIPS.items():
            desc = f"R$ {vip_info['preco']:,} - {vip_info['beneficios'][0][:50]}"
            options.append(
                discord.SelectOption(
                    label=vip_info['nome'],
                    description=desc,
                    emoji=vip_info['emoji'],
                    value=vip_id
                )
            )
        
        super().__init__(placeholder="Escolha um plano VIP...", options=options, row=0)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['erro']} Este não é seu painel!", ephemeral=True)
            return
        
        vip_id = self.values[0]
        vip_info = VIPS[vip_id]
        user_data = get_user_data(self.user_id)
        
        if user_data.get("vip") == vip_id:
            await interaction.response.send_message(f"{EMOJIS['erro']} Você já possui este VIP!", ephemeral=True)
            return
        
        if user_data["carteira"] < vip_info["preco"]:
            falta = vip_info["preco"] - user_data["carteira"]
            await interaction.response.send_message(
                f"{EMOJIS['erro']} Saldo insuficiente! Faltam **R$ {falta:,}**",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title=f"{vip_info['emoji']} Confirmar Compra",
            description=f"Você está prestes a comprar o **{vip_info['nome']}**",
            color=vip_info["cor"]
        )
        
        beneficios_text = "\n".join([f"✅ {b}" for b in vip_info["beneficios"]])
        embed.add_field(name="Benefícios", value=beneficios_text, inline=False)
        embed.add_field(name="Preço", value=f"**R$ {vip_info['preco']:,}**", inline=True)
        embed.add_field(name="Seu Saldo", value=f"R$ {user_data['carteira']:,}", inline=True)
        embed.set_footer(text="Clique em 'Confirmar' para concluir a compra")
        
        view = ConfirmarVIPView(self.user_id, vip_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ConfirmarVIPView(discord.ui.View):
    def __init__(self, user_id, vip_id):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.vip_id = vip_id
    
    @discord.ui.button(label="Confirmar Compra", emoji="✅", style=discord.ButtonStyle.success)
    async def confirmar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['erro']} Esta não é sua compra!", ephemeral=True)
            return
        
        user_data = get_user_data(self.user_id)
        vip_info = VIPS[self.vip_id]
        
        if user_data["carteira"] < vip_info["preco"]:
            await interaction.response.send_message(f"{EMOJIS['erro']} Saldo insuficiente!", ephemeral=True)
            return
        
        user_data["carteira"] -= vip_info["preco"]
        user_data["vip"] = self.vip_id
        
        if vip_info["cargo_id"]:
            try:
                cargo = interaction.guild.get_role(vip_info["cargo_id"])
                if cargo:
                    await interaction.user.add_roles(cargo)
            except Exception as e:
                print(f"Erro ao adicionar cargo VIP: {e}")
        
        save_data(data)
        
        embed = discord.Embed(
            title=f"{EMOJIS['sucesso']} Compra Realizada!",
            description=f"Parabéns! Você adquiriu o **{vip_info['emoji']} {vip_info['nome']}**!",
            color=vip_info["cor"]
        )
        
        embed.add_field(
            name="💰 Dinheiro no Jogo",
            value=f"Você receberá **R$ {vip_info['dinheiro_jogo']:,}** no servidor!",
            inline=False
        )
        
        beneficios_text = "\n".join([f"✅ {b}" for b in vip_info["beneficios"]])
        embed.add_field(name="🎁 Benefícios Ativados", value=beneficios_text, inline=False)
        embed.add_field(name="💳 Saldo Restante", value=f"R$ {user_data['carteira']:,}", inline=True)
        embed.set_footer(text="🎮 Entre no servidor para receber seus benefícios!")
        
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Cancelar", emoji="❌", style=discord.ButtonStyle.danger)
    async def cancelar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{EMOJIS['erro']} Esta não é sua compra!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="❌ Compra Cancelada",
            description="A compra do VIP foi cancelada.",
            color=discord.Color.red()
        )
        await interaction.response.edit_message(embed=embed, view=None)

# ============ EVENTOS ============

@bot.event
async def on_ready():
    print(f'✅ {bot.user} está online e pronto!')
    verificar_daily.start()
    try:
        synced = await bot.tree.sync()
        print(f'Slash commands sincronizados: {len(synced)} comandos.')
    except Exception as e:
        print(f'Erro ao sincronizar comandos: {e}')

@tasks.loop(hours=1)
async def verificar_daily():
    save_data(data)

# ============ COMANDOS PRINCIPAIS ============

@bot.tree.command(name="saldo", description="💰 Veja seu saldo completo")
async def saldo(interaction: discord.Interaction, usuario: discord.Member = None):
    usuario = usuario or interaction.user
    user_data = get_user_data(usuario.id)
    
    total = user_data["carteira"] + user_data["banco"]
    
    embed = discord.Embed(
        title=f"💰 Saldo de {usuario.display_name}",
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url=usuario.display_avatar.url)
    
    embed.add_field(
        name=f"{EMOJIS['carteira']} Carteira",
        value=f"```R$ {user_data['carteira']:,}```",
        inline=True
    )
    embed.add_field(
        name=f"{EMOJIS['banco']} Banco",
        value=f"```R$ {user_data['banco']:,}```",
        inline=True
    )
    embed.add_field(
        name=f"{EMOJIS['dinheiro']} Total",
        value=f"```R$ {total:,}```",
        inline=True
    )
    
    embed.set_footer(text="💡 Use /perfil para ver informações completas")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="perfil", description="📊 Veja seu perfil completo na economia")
async def perfil(interaction: discord.Interaction, usuario: discord.Member = None):
    usuario = usuario or interaction.user
    user_data = get_user_data(usuario.id)
    
    total = user_data["carteira"] + user_data["banco"]
    trabalho_atual = user_data["trabalho"] or "Desempregado"
    
    tem_anel = "anel_supremo" in user_data["inventario"]
    
    embed = discord.Embed(
        title=f"{EMOJIS['coroa']} Perfil de {usuario.display_name}",
        color=discord.Color.gold() if tem_anel else discord.Color.blue(),
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=usuario.display_avatar.url)
    
    if tem_anel:
        embed.description = "💍 **PORTADOR DO ANEL SUPREMO** 💍\n⚡ Poder Absoluto Concedido ⚡\n"
    
    embed.add_field(name=f"{EMOJIS['carteira']} Carteira", value=f"**R$ {user_data['carteira']:,}**", inline=True)
    embed.add_field(name=f"{EMOJIS['banco']} Banco", value=f"**R$ {user_data['banco']:,}**", inline=True)
    embed.add_field(name=f"{EMOJIS['dinheiro']} Patrimônio", value=f"**R$ {total:,}**", inline=True)
    embed.add_field(name=f"{EMOJIS['trabalho']} Profissão", value=f"**{trabalho_atual.title()}**", inline=True)
    embed.add_field(name=f"{EMOJIS['estrela']} Nível", value=f"**{user_data['nivel']}** ({user_data['xp']} XP)", inline=True)
    embed.add_field(name=f"{EMOJIS['diamante']} Reputação", value=f"**{user_data['reputacao']}**", inline=True)
    
    if user_data["celular"]:
        embed.add_field(name=f"{EMOJIS['celular']} Celular", value=f"✅ **{len(user_data['apps'])} apps instalados**", inline=False)
    
    embed.set_footer(text="💼 Sistema de Economia Realista")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="daily", description="🎁 Receba seu auxílio diário do governo")
async def daily(interaction: discord.Interaction):
    user_data = get_user_data(interaction.user.id)
    
    if user_data["ultimo_daily"]:
        ultimo = datetime.fromisoformat(user_data["ultimo_daily"])
        if datetime.now() - ultimo < timedelta(days=1):
            tempo_restante = timedelta(days=1) - (datetime.now() - ultimo)
            horas = tempo_restante.seconds // 3600
            minutos = (tempo_restante.seconds % 3600) // 60
            
            embed = discord.Embed(
                title=f"{EMOJIS['relogio']} Aguarde!",
                description=f"Você já recebeu seu auxílio hoje!\n\n**Próximo daily em:** {horas}h {minutos}min",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
    
    bonus = random.randint(800, 1500)
    user_data["carteira"] += bonus
    user_data["ultimo_daily"] = datetime.now().isoformat()
    user_data["xp"] += 10
    save_data(data)
    
    embed = discord.Embed(
        title=f"{EMOJIS['presente']} Auxílio Governamental Recebido!",
        description=f"O governo depositou seu benefício diário!\n\n**+ R$ {bonus:,}** foram adicionados à sua carteira.",
        color=discord.Color.green()
    )
    embed.set_footer(text="💚 Volte amanhã para receber novamente!")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="trabalhar", description="💼 Trabalhe na sua profissão e ganhe dinheiro")
async def trabalhar(interaction: discord.Interaction):
    user_data = get_user_data(interaction.user.id)
    
    if not user_data["trabalho"]:
        embed = discord.Embed(
            title=f"{EMOJIS['alerta']} Você está desempregado!",
            description="Use `/empregos` para ver vagas disponíveis!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if user_data["ultimo_trabalho"]:
        ultimo = datetime.fromisoformat(user_data["ultimo_trabalho"])
        tempo_espera = TRABALHOS[user_data["trabalho"]]["tempo"]
        if datetime.now() - ultimo < timedelta(seconds=tempo_espera):
            tempo_restante = timedelta(seconds=tempo_espera) - (datetime.now() - ultimo)
            minutos = tempo_restante.seconds // 60
            
            embed = discord.Embed(
                title=f"{EMOJIS['relogio']} Você está cansado!",
                description=f"Descanse um pouco antes de trabalhar novamente.\n\n**Tempo restante:** {minutos} minutos",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
    
    trabalho_info = TRABALHOS[user_data["trabalho"]]
    salario = trabalho_info["salario"]
    
    bonus_multiplier = 1.0
    if "pc_gamer" in user_data["inventario"]:
        bonus_multiplier += 0.2
    
    salario = int(salario * bonus_multiplier)
    
    user_data["carteira"] += salario
    user_data["ultimo_trabalho"] = datetime.now().isoformat()
    user_data["xp"] += 20
    save_data(data)
    
    frases = [
        "Você concluiu seu turno com excelência!",
        "Trabalho árduo sempre traz recompensas!",
        "Mais um dia produtivo na sua carreira!",
        "Seu esforço foi reconhecido e recompensado!",
        "Parabéns pelo trabalho bem feito!"
    ]
    
    embed = discord.Embed(
        title=f"{trabalho_info['emoji']} Trabalho Concluído!",
        description=f"{random.choice(frases)}\n\n**Salário recebido:** R$ {salario:,}",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"💼 Profissão: {user_data['trabalho'].title()}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="empregos", description="📋 Veja e candidate-se a empregos")
async def empregos(interaction: discord.Interaction):
    user_data = get_user_data(interaction.user.id)
    
    embed = discord.Embed(
        title=f"{EMOJIS['trabalho']} Central de Empregos",
        description="Escolha uma profissão e construa sua carreira!\n\nUse o menu abaixo para se candidatar:",
        color=discord.Color.blue()
    )
    
    for nome, info in TRABALHOS.items():
        tempo_horas = info["tempo"] // 3600
        disponivel = user_data["nivel"] >= info["nivel_min"]
        status = "✅ Disponível" if disponivel else f"🔒 Nível {info['nivel_min']} necessário"
        
        embed.add_field(
            name=f"{info['emoji']} {nome.title()}",
            value=f"**Salário:** R$ {info['salario']:,}\n**Tempo:** {tempo_horas}h\n**Status:** {status}",
            inline=True
        )
    
    view = EmpregosView(interaction.user.id)
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="loja", description="🛍️ Veja e compre itens da loja")
async def loja(interaction: discord.Interaction):
    embed = discord.Embed(
        title=f"{EMOJIS['diamante']} Loja de Luxo",
        description="Invista em itens que trarão benefícios!\n\nUse o menu abaixo para comprar:",
        color=discord.Color.purple()
    )
    
    for item, info in LOJA.items():
        if info.get("secreto"):
            continue
            
        embed.add_field(
            name=f"{info['emoji']} {item.replace('_', ' ').title()}",
            value=f"**Preço:** R$ {info['preco']:,}\n{info['descricao']}",
            inline=True
        )
    
    view = LojaView(interaction.user.id)
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="celular", description="📱 Acesse seu smartphone com interface completa")
async def celular(interaction: discord.Interaction):
    user_data = get_user_data(interaction.user.id)
    
    if not user_data["celular"] and "celular" not in user_data["inventario"]:
        embed = discord.Embed(
            title=f"{EMOJIS['erro']} Você não tem um celular!",
            description="Compre um celular na `/loja` para desbloquear esta funcionalidade!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if not user_data["celular"]:
        user_data["celular"] = True
        save_data(data)
    
    embed = discord.Embed(
        title=f"{EMOJIS['celular']} Meu Smartphone",
        description="📱 Seu hub central para tudo!\n\nEscolha um app abaixo:",
        color=discord.Color.blue()
    )
    embed.add_field(name="📱 Modelo", value="iPhone 15 Pro Max", inline=True)
    embed.add_field(name="📦 Apps Instalados", value=str(len(user_data["apps"])), inline=True)
    embed.add_field(name="🔋 Bateria", value="100%", inline=True)
    embed.set_footer(text="💡 Dica: Explore a Play Store e o Mercado Negro!")
    
    view = CelularView(interaction.user.id)
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="inventario", description="🎒 Veja seus itens")
async def inventario(interaction: discord.Interaction):
    user_data = get_user_data(interaction.user.id)
    
    embed = discord.Embed(
        title=f"{EMOJIS['diamante']} Seu Inventário",
        color=discord.Color.blue()
    )
    
    if not user_data["inventario"]:
        embed.description = "Seu inventário está vazio! Visite a `/loja` para comprar itens."
    else:
        for item in user_data["inventario"]:
            if item in LOJA:
                info = LOJA[item]
                embed.add_field(
                    name=f"{info['emoji']} {item.replace('_', ' ').title()}",
                    value=info['descricao'],
                    inline=False
                )
            elif item in MERCADO_NEGRO:
                info = MERCADO_NEGRO[item]
                embed.add_field(
                    name=f"{info['emoji']} {item.replace('_', ' ').title()}",
                    value=info['descricao'],
                    inline=False
                )
    
    await interaction.response.send_message(embed=embed)


if __name__ == '__main__':
    import sys

    # Allow token to be provided as first CLI argument for convenience:
    #   python main.py <TOKEN>
    # Fallback: BOT_TOKEN environment variable (or .env via python-dotenv)
    token = None
    if len(sys.argv) > 1 and sys.argv[1].strip():
        token = sys.argv[1].strip()
    else:
        token = os.environ.get('BOT_TOKEN')

    if not token:
        print('ERROR: No token provided. You can run: python main.py <TOKEN> or set BOT_TOKEN in environment/.env')
    else:
        bot.run(token)