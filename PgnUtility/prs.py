# -*- coding: utf-8 -*-
"""
prs.py

Cutechess pgn result summarizer

Read cutechess pgn output and generate result info including time forfeit
stalled connections, win, draws and loses and others.

Requirements:
    python 3

"""


import argparse
try:
    import statistics as stats
except ImportError as err:
    print('{}, please use python 3.'.format(err))


def get_players(data):
    """ Read data and return unique player names """
    players = []
    for n in data:
        players.append(n[0])
        
    return sorted(list(set(players)))


def process_pgn(pgnfn):
    """
    Read pgnfn and print result stats
    """
    data = [] 
    t_games = 0    
    ter = None

    with open(pgnfn, 'r') as f:
        for lines in f:
            line = lines.rstrip()
            if '[White ' in line:
                wp = line.split('"')[1]                
            elif '[Black ' in line:
                bp = line.split('"')[1]
            elif '[Result ' in line:
                res = line.split('"')[1]
            elif '[PlyCount ' in line:
                ply_count = int(line.split('"')[1])
            elif '[Termination ' in line:
                ter = line.split('"')[1]
            elif '[TimeControl ' in line:
                ister = ter if ter is not None else None
                if res == '1-0':
                    t_games += 1
                elif res == '0-1':
                    t_games += 1
                else:
                    t_games += 1
                    
                # color 0 = white, 1 = black
                # [name, color, win, loss, draw, win_ply_count, tf, sc]
                # tf = time forfeit, sc = stalled connection
                # Only record the ply_count for the player that won
                if ister:
                    if res == '1-0':
                        if ter == 'time forfeit':
                            data.append([bp, 1, 0, 1, 0, 0, 1, 0])
                        elif ter == 'stalled connection':
                            data.append([bp, 1, 0, 1, 0, 0, 0, 1])
                        else:
                            data.append([bp, 1, 0, 1, 0, 0, 0, 0])
                        data.append([wp, 0, 1, 0, 0, ply_count, 0, 0])
                    elif res == '0-1':
                        if ter == 'time forfeit':
                            data.append([wp, 0, 0, 1, 0, 0, 1, 0])
                        elif ter == 'stalled connection':
                            data.append([wp, 0, 0, 1, 0, 0, 0, 1])
                        else:
                            data.append([wp, 0, 0, 1, 0, 0, 0, 0])
                        data.append([bp, 1, 1, 0, 0, ply_count, 0, 0])
                    elif res == '1/2-1/2':
                        data.append([wp, 0, 0, 0, 1, 0, 0, 0])
                        data.append([bp, 1, 0, 0, 1, 0, 0, 0])
                else:
                    if res == '1-0':
                        data.append([bp, 1, 0, 1, 0, 0, 0, 0])
                        data.append([wp, 0, 1, 0, 0, ply_count, 0, 0])
                    elif res == '0-1':
                        data.append([wp, 0, 0, 1, 0, 0, 0, 0])
                        data.append([bp, 1, 1, 0, 0, ply_count, 0, 0])
                    elif res == '1/2-1/2':
                        data.append([wp, 0, 0, 0, 1, 0, 0, 0])
                        data.append([bp, 1, 0, 0, 1, 0, 0, 0])                    
                ter = None

    players = get_players(data)

    print('File: {}\n'.format(pgnfn))

    # (1) Summary table    
    print('{:28.27}: {:>6s} {:>6s} {:>6s} {:>5s} {:>5s} {:>5s} {:>3s} {:>3s}'.
          format('Name','Games','Pts','Pts%','Win','Loss','Draw','Tf','Sc'))

    for p in players:
        g = 0
        pts, wwins, bwins, wloss, bloss, draws, tf, sc = 0, 0, 0, 0, 0, 0, 0, 0
        for n in data:
            if p == n[0]:
                pts += n[2] + n[4]/2.
                tf += n[6]
                sc += n[7]
                draws += n[4]
                if n[1] == 0:
                    wwins += n[2]
                    wloss += n[3]
                else:
                    bwins += n[2]
                    bloss += n[3]
                g += 1
        pct = 0.0
        if g:
            pct = 100*(wwins+bwins + draws/2) / g

        print('{:28.27}: {:>6d} {:>6.1f} {:>6.1f} {:>5d} {:>5d} {:>5d} {:>3d} '
              '{:>3d}'.format(p,g,pts,pct,wwins+bwins,wloss+bloss,draws,tf,sc))

    # (2) White wins and Black wins table
    print()
    print('{:28.27}: {:>6s} {:>6s} {:>6s}'.format('Name', 'W_win',
                                              'B_win', 'Draw'))
    t_wwins, t_bwins, t_draws = 0, 0, 0
    for p in players:
        pts, wwins, bwins, wloss, bloss, draws = 0, 0, 0, 0, 0, 0
        for n in data:
            if p == n[0]:
                pts += n[2] + n[4]/2
                if n[1] == 0:
                    wwins += n[2]
                    wloss += n[3]
                    t_wwins += n[2]
                else:
                    bwins += n[2]
                    bloss += n[3]
                    t_bwins += n[2]
                draws += n[4]
                t_draws += n[4]

        print('{:28.27}: {:6d} {:6d} {:6d}'.format(p, wwins, bwins, draws))
        
    # (3) Win ply count table
    print()
    print('{:28.27}: {:>6s} {:>6s}'.format('Name', 'Wapc', 'Sd'))
    for p in players:
        winplycount = []
        for n in data:
            if p == n[0]:
                winplycount.append(n[5])

        print('{:28.27}: {:>6.0f} {:>6.0f}'.format(p, stats.mean(winplycount),
                                                    stats.stdev(winplycount)))
        
    print()
    print('Total games : {}'.format(t_games))
    print('White wins  : {} ({:0.1f}%)'.format(t_wwins, 100*t_wwins/t_games))
    print('Black wins  : {} ({:0.1f}%)'.format(t_bwins, 100*t_bwins/t_games))
    print('Draws       : {} ({:0.1f}%)'.format(t_draws, 100*t_draws/t_games))
    
    # (4) Legend
    print()
    print('Tf = time forfeit')
    print('Sc = stalled connection')
    print('Wapc = win average ply count, lower is better')
    print('Sd = standard deviation\n')


def main():
    parser = argparse.ArgumentParser(add_help=False,
    description='About: Read cutechess pgn file and output results summary.')
    parser.add_argument('-p', '--pgn', help='input cutechess pgn filename',
                        required=True)
    parser.add_argument('-h', '--help', action='help',
                default=argparse.SUPPRESS,
                help='will show this help, use python 3 to run this script')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s v0.1.0')

    args = parser.parse_args()
    
    process_pgn(args.pgn)


if __name__ == "__main__":
    main()

