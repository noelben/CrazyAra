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


VERSION = '0.2.0'
WHITE = 0
BLACK = 1


def get_players(data):
    """ Read data and return unique player names """
    players = []
    for n in data:
        players.append(n[0])

    return sorted(list(set(players)))


def get_game_headers(pgn):
    """
    Read pgn and return a list of header dict
    """
    h = []
    ter = '?'
    
    with open(pgn, 'r') as f:
        for lines in f:
            line = lines.rstrip()
            if '[White ' in line:
                wp = line.split('"')[1]
            elif '[Black ' in line:
                bp = line.split('"')[1]
            elif '[Result ' in line:
                res = line.split('"')[1]
            elif '[PlyCount ' in line:
                ply = int(line.split('"')[1])
            elif '[Termination ' in line:
                ter = line.split('"')[1]
            elif '[TimeControl ' in line or '[WhiteTimeControl ' in line:
                # WhiteTimeControl would appear when TC are different
                d = {
                    'White': wp,
                    'Black': bp,
                    'Result': res,
                    'Termination': ter,
                    'PlyCount': ply
                }
                h.append(d)
                ter = '?'

    return h


def save_win(data, name, color, ply):
    """
    """
    data.append([name, color, 1, 0, 0, ply, 0, 0])


def save_draw(data, name, color):
    """
    """
    data.append([name, color, 0, 0, 1, 0, 0, 0])


def save_loss(data, ter, name, color):
    """
    """
    if ter != '?':
        if ter == 'time forfeit':
            data.append([name, color, 0, 1, 0, 0, 1, 0])
        elif ter == 'stalled connection':
            data.append([name, color, 0, 1, 0, 0, 0, 1])
        else:
            # Other reason of lossing
            data.append([name, color, 0, 1, 0, 0, 0, 0])
    else:
        data.append([name, color, 0, 1, 0, 0, 0, 0])


def extract_info(data, ter, wp, bp, res, ply):
    """       
    """
    # color 0 = white, 1 = black
    # [name, color, win, loss, draw, win_ply_count, tf, sc]
    # tf = time forfeit, sc = stalled connection
    # Only record the ply_count for the player that won

    if ter != '?':
        if res == '1-0':
            save_loss(data, ter, bp, BLACK)
            save_win(data, wp, WHITE, ply)
        elif res == '0-1':
            save_loss(data, ter, wp, WHITE)
            save_win(data, bp, BLACK, ply)
        elif res == '1/2-1/2':
            save_draw(data, wp, WHITE)
            save_draw(data, bp, BLACK)
    else:
        if res == '1-0':
            save_loss(data, ter, bp, BLACK)
            save_win(data, wp, WHITE, ply)
        elif res == '0-1':
            save_loss(data, ter, wp, WHITE)
            save_win(data, bp, BLACK, ply)
        elif res == '1/2-1/2':
            save_draw(data, wp, WHITE)
            save_draw(data, bp, BLACK)

    return data


def print_summary(players, data):
    """
    """
    # (1) Summary table    
    print('{:28.27}: {:>6s} {:>6s} {:>6s} {:>5s} {:>5s} {:>5s} {:>3s} {:>3s}'.
          format('Name','Games','Pts','Pts%','Win','Loss','Draw','Tf','Sc'))

    for p in players:
        g = 0
        pts, wwins, bwins, wloss, bloss, draws, tf, sc = 0,0,0,0,0,0,0,0
        
        # [name, color, win, loss, draw, win_ply_count, tf, sc]
        for n in data:
            if p == n[0]:
                pts += n[2] + n[4]/2.
                tf += n[6]
                sc += n[7]
                draws += n[4]
                if n[1] == WHITE:
                    wwins += n[2]
                    wloss += n[3]
                else:
                    bwins += n[2]
                    bloss += n[3]
                g += 1
        pct = 0.0
        if g:
            pct = 100*(wwins+bwins + draws/2) / g

        print('{:28.27}: {:>6d} {:>6.1f} {:>6.1f} {:>5d} {:>5d} '
              '{:>5d} {:>3d} {:>3d}'.
              format(p,g,pts,pct,wwins+bwins,wloss+bloss,draws,tf,sc))


def print_wins(players, data):
    """
    """
    # (1) Wins / Draws table
    t_wwins, t_bwins, t_draws = 0, 0, 0
    print('{:28.27}: {:>6s} {:>6s} {:>6s}'.
          format('Name', 'W_win', 'B_win', 'Draw'))
    for p in players:
        pts, wwins, bwins, wloss, bloss, draws = 0, 0, 0, 0, 0, 0
        
        # [name, color, win, loss, draw, win_ply_count, tf, sc]
        for n in data:
            if p == n[0]:
                pts += n[2] + n[4]/2
                if n[1] == WHITE:
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

    return t_wwins, t_bwins, t_draws

        
def print_win_ply(players, data):
    """
    """
    # (3) Win ply count table
    print()
    print('{:28.27}: {:>6s} {:>6s}'.format('Name', 'Wapc', 'Sd'))
    for p in players:
        winplycount = []
        
        # [name, color, win, loss, draw, win_ply_count, tf, sc]
        for n in data:
            if p == n[0]:
                winplycount.append(n[5])
                
        if len(winplycount) > 1:
            print('{:28.27}: {:>6.0f} {:>6.0f}'.format(p, stats.mean(winplycount),
                                                    stats.stdev(winplycount)))


def process_pgn(pgnfn):
    """
    Read pgnfn and print result stats
    """
    data = []
    f_games, u_games = 0, 0  # f_games = finished games, u = unfinished
    
    game_headers = get_game_headers(pgnfn)
    for h in game_headers:
        wp = h['White']
        bp = h['Black']
        res = h['Result']
        ter = h['Termination']
        ply = h['PlyCount']

        if res == '1-0' or res == '0-1' or res == '1/2-1/2':
            f_games += 1
            # Extract info from this game header and save it to data
            extract_info(data, ter, wp, bp, res, ply)
        else:
            u_games += 1

    players = get_players(data)
    print('File: {}\n'.format(pgnfn))    
    print_summary(players, data)
    print()    
    t_wwins, t_bwins, t_draws = print_wins(players, data)
    print()    
    print_win_ply(players, data)
    print()

    # Overall game summary
    print('Finished games   : {}'.format(f_games))
    print('White wins       : {} ({:0.1f}%)'.format(t_wwins,
          100*t_wwins/f_games))
    print('Black wins       : {} ({:0.1f}%)'.format(t_bwins,
          100*t_bwins/f_games))
    print('Draws            : {} ({:0.1f}%)'.format(t_draws,
          100*t_draws/f_games))
    print('Unfinished games : {} ({:0.1f}%)'.format(u_games,
          100*u_games/(f_games+u_games)))
    
    # Legend
    print()
    print('Tf = time forfeit')
    print('Sc = stalled connection')
    print('Wapc = win average ply count, lower is better')
    print('Sd = standard deviation\n')


def main():
    parser = argparse.ArgumentParser(add_help=False,
             description='About: Read cutechess pgn file and output \
             results summary.')
    parser.add_argument('-p', '--pgn', help='input cutechess pgn filename, \
                        default is mygames.pgn',
                        default='mygames.pgn', required=False)
    parser.add_argument('-h', '--help', action='help',
                default=argparse.SUPPRESS,
                help='will show this help, use python 3 to run this script')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s {}'.format(VERSION))

    args = parser.parse_args()
    
    process_pgn(args.pgn)


if __name__ == "__main__":
    main()

