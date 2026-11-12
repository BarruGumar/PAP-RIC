# Estudos — visual e corpo do RIC

**Data:** 2026-11-12  
**Para quê:** decidir o aspeto do companheiro. O corpo com pernas, braços ou locomoção continua fora do caminho desta PAP. O que entra agora é o rosto e, se houver material reaproveitado, um suporte simples.

Três textos. O de Halicka e Surel está em PDF nesta pasta, licença CC BY-NC 4.0. Os outros dois são da Springer: fica aqui o que dizem e a ligação, não o artigo inteiro.

## 1. Oh, Oh e Ju (2019) — preferência de forma

Suyeon Oh, Young Hoon Oh e Da Young Ju, Yonsei University. «Understanding the Preference of the Elderly for Companion Robot Design». Conferência AHFE 2019. DOI: [10.1007/978-3-030-20467-9_9](https://doi.org/10.1007/978-3-030-20467-9_9). Ficha: [Yonsei](https://yonsei.elsevierpure.com/en/publications/understanding-the-preference-of-the-elderly-for-companion-robot-d/).

Entrevistaram 19 pessoas de idades diferentes sobre cinco conceitos de robô companheiro.

- As pessoas mais velhas preferiram formas **redondas** e **antropomórficas** (com traços de pessoa).
- Na aparência, o que contava era um desenho **íntimo**, que desse vontade de falar com o robô.
- Os adultos mais novos preferiram um desenho **limpo**, com poucos pormenores, e pensaram na manutenção e na higiene.

Para o RIC: o rosto no ecrã deve ser redondo, com olhos e boca simples, e o conjunto deve parecer alguém com quem se fala. Poucos botões, pouco ruído visual. Não é um painel de controlo.

## 2. Sun e Jin (2021) — abstrato ou figurativo

Xinxin Sun e Wenkui Jin. «Elderly’s preferences towards rehabilitation robot appearance using electroencephalogram signal». *EURASIP Journal on Advances in Signal Processing*. 2021. Acesso aberto: [10.1186/s13634-021-00757-z](https://link.springer.com/article/10.1186/s13634-021-00757-z).

Dez pessoas com cerca de 61 anos viram dez robôs do mercado. O grupo abstrato parece uma máquina com traços humanos estilizados (olhos, orelhas, sobrancelhas). O grupo figurativo aproxima-se de um corpo humano real, com braços, mãos e pernas. Mediram o gosto (gosto / neutro / não gosto) e o eletroencefalograma.

- Robôs abstratos: gosto 74,4 %, neutro 16,7 %, não gosto 8,9 %. Razões: «giro», «simples e honesto», «fácil de abordar».
- Robôs figurativos: gosto 13,3 %, neutro 25,6 %, não gosto 61,1 %. Razões: «pânico», «volumoso», «hostil».
- O figurativo, demasiado parecido com uma pessoa, cai no vale da estranheza. Uma diferença pequena em relação a um humano torna-se a coisa que se nota.
- Um robô que não é uma pessoa é tratado mais como um animal de companhia: tolera-se que não seja perfeito.
- Se a aparência promete um humano, a pessoa espera comportamento humano. Se a aparência é de máquina com cara, a expectativa desce e a convivência fica mais fácil.
- Conclusão dos autores: o protótipo deve ser antropomórfico e, ao mesmo tempo, parecer uma máquina. Para a reabilitação, sugerem pensá-lo como um eletrodoméstico inteligente, para não acentuar as limitações da pessoa.

A amostra é pequena (dez pessoas) e o tema é robô de reabilitação, não um companheiro de conversa. Mesmo assim, o resultado de gosto é claro e combina com Oh, Oh e Ju: cara de companheiro, corpo que não imita uma pessoa.

## 3. Halicka e Surel (2022) — Rudy e smart living

Katarzyna Halicka e Dariusz Surel. «Smart living technologies in the context of improving the quality of life for older people: the case of the humanoid Rudy robot». *Human Technology*, 18(2), 2022, 191–208. DOI: [10.14254/1795-6889.2022.18-2.5](https://doi.org/10.14254/1795-6889.2022.18-2.5). Licença CC BY-NC 4.0. Cópia: [`halicka-surel-2022-rudy-smart-living.pdf`](halicka-surel-2022-rudy-smart-living.pdf).

Inquérito na Polónia a 1152 pessoas com mais de 40 anos. Não usaram o Rudy. Avaliaram a descrição, fotos e filmes. O Rudy lembra medicamentos, pode doseá-los, monitoriza o paciente à distância, chama ajuda, procura objetos, transporta coisas, propõe jogos, música e dança, e faz companhia.

Exemplos de corpo que o artigo usa para comparar:

| Robô | Corpo | O que interessa ao RIC |
|---|---|---|
| Pepper | Cerca de 120 cm. Ecrã tátil no peito. Microfones, sensores, luzes. | Altura de conversa. A cara e o ecrã são o contacto. |
| Care-O-bot 3 | Braço, garra, tabuleiro, tronco que gesticula. | Fora desta PAP. |
| Cody | Base móvel, braços, tronco que sobe. | Fora desta PAP. |

Funcionalidades que o artigo destaca como as que facilitam a vida: avisar a família, monitorização à distância, vigilância da casa, prevenir e detetar quedas, emergência sem contacto, entretenimento (anedotas, dança) e interação.

Critérios mais importantes para os inquiridos: técnicos (76,8 %) e procura da tecnologia (70,4 %). Os sociais e éticos e os ecológicos também pesam. O Rudy teve a nota mais alta no potencial de melhorar (média 5,20 em 7) e a mais baixa na probabilidade de problemas técnicos graves (3,65) e em materiais caros e difíceis (3,80). Pessoas com mais de 60 anos deram cerca de 5,0 à facilidade de uso face ao que já existe.

O RIC não diagnostica, não mede a saúde, não deteta quedas e não avisa familiares. Essas funções do Rudy ficam de fora. O que se aproveita é o resto: interação, entretenimento, uso simples, e um corpo que não dependa de peças caras. Reaproveitar o tablet e o PC responde ao critério ecológico e ao medo de avarias.

## O que isto muda no visual

O protótipo já tem um rosto redondo, olhos e boca, em `ric/web/index.html` (estados a ouvir, a pensar e a avisar). Os estudos pedem que esse rosto continue a ser o centro, e que o corpo não compita com ele.

Nesta PAP o corpo, se existir, é um suporte parado:

- O ecrã é a cabeça. Tablet reaproveitado, na vertical, à altura de quem está sentado. O Pepper usa cerca de 120 cm como referência de conversa, não como medida obrigatória.
- A cara é abstrata: círculo, dois olhos, uma boca. Sem fotografia de pessoa, sem pele, sem dentes.
- O corpo à volta do ecrã pode ser uma caixa, um candeeiro velho ou um suporte de monitor. Lê-se como objeto de casa, não como manequim.
- Braços, pernas, rodas e dança não entram. O artigo do Rudy mostra que isso existe noutros robôs e que as pessoas temem a complexidade técnica.

O ecrã, quando se trabalhar o visual, mantém texto grande, poucos controlos e o alerta do lembrete por cima da conversa. O rosto muda de estado quando ouve, pensa ou avisa, para se perceber que está presente sem precisar de um corpo que se mexa.
