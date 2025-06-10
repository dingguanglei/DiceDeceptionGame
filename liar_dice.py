import random

class Player:
    def __init__(self, name, is_human=False, personality=None):
        self.name = name
        self.is_human = is_human
        self.personality = personality
        self.dice = []

    def roll_dice(self, num=5):
        self.dice = [random.randint(1, 6) for _ in range(num)]

    def count_value(self, value):
        return self.dice.count(value)

    def show_dice(self):
        return ' '.join(str(d) for d in self.dice)

PHRASES = {
    '理性派': ['我根据概率来看...', '仔细想想应该这样。', '冷静分析，这是个好选择。'],
    '豪赌客': ['哈哈，再来点刺激的！', '赌一把大的！', '不怕，你们跟不上我的节奏。'],
    '滑头鬼': ['也许是这样？', '你们最好相信我。', '呵呵，真相可不好说。'],
    '神秘人': ['......', '嗯。', '随你怎么想。']
}

class LiarDiceGame:
    def __init__(self, num_ai=4):
        self.players = [Player('玩家', True)]
        personalities = ['理性派', '豪赌客', '滑头鬼', '神秘人']
        for i in range(num_ai):
            p = personalities[i % len(personalities)]
            self.players.append(Player(f'AI{i+1}-{p}', False, p))
        self.current_player = 0
        self.last_call = None  # (count, face)

    def next_player(self):
        self.current_player = (self.current_player + 1) % len(self.players)
        return self.players[self.current_player]

    def is_higher_call(self, count, face):
        if self.last_call is None:
            return True
        last_count, last_face = self.last_call
        return count > last_count or (count == last_count and face > last_face)

    def total_count(self, face):
        return sum(p.count_value(face) for p in self.players)

    def ai_decision(self, player):
        if self.last_call is None:
            # first call
            count = random.randint(1, 3)
            face = random.randint(1, 6)
            phrase = random.choice(PHRASES.get(player.personality, ['']))
            print(f'{player.name}: {phrase}')
            return ('call', count, face)
        last_count, last_face = self.last_call
        # simple strategy: 50% chance to challenge if call seems unlikely
        estimate = sum(p.count_value(last_face) for p in [player])
        if estimate + 2 < last_count and random.random() < 0.5:
            phrase = random.choice(PHRASES.get(player.personality, ['']))
            print(f'{player.name}: {phrase}')
            return ('challenge',)
        # otherwise make a higher call
        count = last_count
        face = last_face
        if face < 6:
            face += 1
        else:
            count += 1
            face = 1
        phrase = random.choice(PHRASES.get(player.personality, ['']))
        print(f'{player.name}: {phrase}')
        return ('call', count, face)

    def human_decision(self, player):
        if self.last_call is None:
            print('当前无喊话，你需要先喊一个(数量 点数)，例如"3 4"表示3个4:')
        else:
            lc, lf = self.last_call
            print(f'当前喊话: {lc}个{lf}点')
            print('输入"c"质疑，或输入更高喊话(数量 点数)，例如"3 5":')
        while True:
            cmd = input('> ').strip()
            if cmd.lower() == 'c' and self.last_call is not None:
                return ('challenge',)
            parts = cmd.split()
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                count = int(parts[0])
                face = int(parts[1])
                if 1 <= face <= 6 and count >= 1 and self.is_higher_call(count, face):
                    return ('call', count, face)
            print('输入无效，请重新输入')

    def play_round(self):
        # roll dice
        for p in self.players:
            p.roll_dice()
        print('--- 新的一轮开始! ---')
        print(f'你的骰子: {self.players[0].show_dice()}')
        self.current_player = 0
        self.last_call = None

        while True:
            player = self.players[self.current_player]
            if player.is_human:
                action = self.human_decision(player)
            else:
                action = self.ai_decision(player)
                if action[0] == 'call':
                    print(f'{player.name} 喊话 {action[1]}个{action[2]}点')
                else:
                    print(f'{player.name} 质疑!')
            if action[0] == 'call':
                self.last_call = (action[1], action[2])
                self.next_player()
            else:
                # challenge
                print('--- 开始揭晓 ---')
                for p in self.players:
                    print(f'{p.name}: {p.show_dice()}')
                count = self.total_count(self.last_call[1])
                print(f'实际共有{count}个{self.last_call[1]}点')
                if count >= self.last_call[0]:
                    loser = player.name
                    print(f'{player.name} 质疑失败!')
                else:
                    loser = self.players[(self.current_player-1) % len(self.players)].name
                    print(f'{self.players[(self.current_player-1)%len(self.players)].name} 喊话失败!')
                print(f'本轮{loser} 失败\n')
                break

    def start(self):
        while True:
            self.play_round()
            if input('继续游戏? (y/n) ').strip().lower() != 'y':
                break

if __name__ == '__main__':
    game = LiarDiceGame()
    game.start()
