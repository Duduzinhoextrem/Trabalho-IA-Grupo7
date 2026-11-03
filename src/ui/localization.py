"""Traduções para português dos termos, atributos e gráficos da interface.

Usa descrições voltadas a quem não conhece IA ou RPG.
"""

from __future__ import annotations

from typing import Any

# Tradução dos tipos de criaturas do D&D 5e
CREATURE_TYPE_TRANSLATIONS: dict[str, str] = {
    "aberration": "Aberração",
    "beast": "Fera / Animal",
    "celestial": "Celestial / Anjo",
    "construct": "Construto / Autômato",
    "dragon": "Dragão",
    "elemental": "Elemental",
    "fey": "Fada / Feérico",
    "fiend": "Ínfero / Demônio",
    "giant": "Gigante",
    "humanoid": "Humanoide",
    "monstrosity": "Monstruosidade",
    "ooze": "Gosma / Lodo",
    "plant": "Planta Monstruosa",
    "undead": "Morto-Vivo",
    "swarm of tiny beasts": "Enxame de Criaturinhas",
}

# Tradução dos tamanhos de criaturas
CREATURE_SIZE_TRANSLATIONS: dict[str, str] = {
    "Tiny": "Minúsculo",
    "Small": "Pequeno",
    "Medium": "Médio",
    "Large": "Grande",
    "Huge": "Enorme",
    "Gargantuan": "Colossal",
}

# Nomes e descrições em português dos 16 genes do algoritmo genético.
GENE_FRIENDLY_INFO: dict[str, dict[str, str]] = {
    "w_weight_str": {
        "nome": "Foco em Força do Guerreiro",
        "explicacao": "Quanto mais alto, mais pontos o guerreiro investe em dar dano físico forte.",
    },
    "w_weight_vit": {
        "nome": "Foco em Vida (Vitalidade) do Guerreiro",
        "explicacao": "Quanto mais alto, mais pontos investidos em barra de vida (HP) para aguentar pancada.",
    },
    "w_weight_def": {
        "nome": "Foco em Defesa do Guerreiro",
        "explicacao": "Quanto mais alto, mais pontos em armadura natural para amortecer o dano recebido.",
    },
    "ally_prio_mage": {
        "nome": "Preferência por contratar Mago",
        "explicacao": "Prioridade de contratar o Mago, que usa ataques mágicos à distância.",
    },
    "ally_prio_archer": {
        "nome": "Preferência por contratar Arqueiro",
        "explicacao": "Prioridade de contratar o Arqueiro (ataques físicos à distância rápidos).",
    },
    "ally_prio_monk": {
        "nome": "Preferência por contratar Monge",
        "explicacao": "Prioridade de contratar o Monge (lutador corpo a corpo resistente que divide a linha de frente).",
    },
    "ally_prio_priest": {
        "nome": "Preferência por contratar Padre (Curandeiro)",
        "explicacao": "Prioridade de contratar o Padre (recupera a vida do grupo durante a batalha).",
    },
    "ally_prio_alchemist": {
        "nome": "Preferência por contratar Alquimista",
        "explicacao": "Prioridade de contratar o Alquimista (fortalece a equipe e enfraquece os inimigos com poções).",
    },
    "ally_weight_power": {
        "nome": "Evolução dos Aliados: Ataque",
        "explicacao": "Fatia dos pontos dos companheiros voltada para aumentar o poder ofensivo.",
    },
    "ally_weight_vit": {
        "nome": "Evolução dos Aliados: Vida",
        "explicacao": "Fatia dos pontos dos companheiros voltada para ter mais pontos de vida.",
    },
    "ally_weight_def": {
        "nome": "Evolução dos Aliados: Defesa",
        "explicacao": "Fatia dos pontos dos companheiros voltada para proteção e sobrevivência.",
    },
    "equip_offense_priority": {
        "nome": "Foco de Compra: Defesa vs. Ataque",
        "explicacao": "Valores baixos (< 0,40) compram Armadura e Escudo primeiro; valores altos compram Armas caras primeiro.",
    },
    "hire_before_equip_discrete": {
        "nome": "Priorizar Aliados antes de Equipamentos",
        "explicacao": "1 = contrata ajudantes assim que liberado; 0 = prefere equipar o guerreiro antes.",
    },
    "min_gold_reserve": {
        "nome": "Reserva de Ouro 'Pé-de-Meia'",
        "explicacao": "Quantidade de moedas de ouro que o personagem NUNCA gasta no mercado, guardando para emergências.",
    },
    "equipment_buy_threshold": {
        "nome": "Paciência para Comprar Equipamentos",
        "explicacao": "Define se compra logo o primeiro item ou se economiza para pular direto para armas/armaduras melhores.",
    },
    "ally_hire_threshold": {
        "nome": "Paciência para Contratar Aliados",
        "explicacao": "Define se contrata o primeiro aliado imediatamente ou se espera ter uma margem de segurança financeira.",
    },
}

# Tradução dos papéis e classes dos aliados
ALLY_CLASS_LABELS: dict[str, dict[str, str]] = {
    "mage": {
        "nome": "Mago",
        "funcao": "Ataque Mágico à Distância",
        "descricao": "Fica na retaguarda e ataca com magias; a defesa e a resistência do alvo ainda afetam o dano.",
    },
    "archer": {
        "nome": "Arqueiro",
        "funcao": "Ataque Físico à Distância",
        "descricao": "Fica na retaguarda com arco e flecha, eliminando inimigos rápidos com precisão.",
    },
    "monk": {
        "nome": "Monge",
        "funcao": "Lutador Espiritual (Linha de Frente)",
        "descricao": "Luta lado a lado com o guerreiro, dividindo os golpes dos monstros e usando artes marciais.",
    },
    "priest": {
        "nome": "Padre / Clérigo",
        "funcao": "Curandeiro e Suporte Vital",
        "descricao": "Cura o guerreiro e os amigos quando a vida fica baixa e golpeia com luz sagrada.",
    },
    "alchemist": {
        "nome": "Alquimista",
        "funcao": "Especialista em Poções (Buff / Debuff)",
        "descricao": "Lança frascos que aumentam o dano dos aliados e corroem a defesa dos monstros.",
    },
}

# Tradução de motivos de encerramento de combate
TERMINATION_REASON_TRANSLATIONS: dict[str, str] = {
    "enemies_defeated": "🏆 Vitória! Todos os monstros da sala foram derrotados",
    "warrior_died": "💀 O Guerreiro foi derrotado em combate (Fim da jornada)",
    "max_turns_exceeded": "⏳ Empate por Exaustão (Atingiu o limite de 40 turnos)",
}

# Tradução de categorias de itens
ITEM_CATEGORY_TRANSLATIONS: dict[str, str] = {
    "weapon": "Arma",
    "armor": "Armadura",
    "shield": "Escudo",
}


def translate_creature_type(type_str: str) -> str:
    """Retorna o tipo de monstro em português."""
    clean = str(type_str).lower().strip()
    return CREATURE_TYPE_TRANSLATIONS.get(clean, type_str.capitalize())


def translate_creature_size(size_str: str) -> str:
    """Retorna o porte da criatura em português."""
    clean = str(size_str).strip()
    return CREATURE_SIZE_TRANSLATIONS.get(clean, size_str)


def translate_reason(reason_str: str) -> str:
    """Traduz o motivo de término de batalha."""
    return TERMINATION_REASON_TRANSLATIONS.get(str(reason_str), str(reason_str))
