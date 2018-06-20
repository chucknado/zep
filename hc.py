import argparse

from zep.zendesk import HelpCenter, Community, KB


def push_dita_html(args):
    """
    :param args: folder_name (str)
    :return: None
    """
    kb = KB('support')  # brand doesn't matter - push is brand-agnostic
    kb.push_transformed_articles(args.folder_name, args.write)


def push_staged(args):
    """
    :param args: folder_name (str), product (str), --write (bool)
    :return: None
    """
    if args.product not in ['support', 'help', 'bime', 'explore', 'chat']:
        print('The product name is invalid. Try again.')
        exit()
    package = KB(args.product)
    package.push_staged(args.folder_name, args.locale, args.write)


def take_inventory(args):
    """
    :param args: product (str), categories (list of ints)
    :return: None
    """
    if args.product not in ['support', 'help', 'bime', 'explore', 'chat']:
        print('The product name is invalid. Try again.')
        exit()
    kb = KB(args.product)
    if args.categories:
        kb.take_inventory(args.categories, excel=True)     # [203664236, 203664226]
    else:
        kb.take_inventory(excel=True)


def update_author(args):
    """
    :param args: product, article id, user id
    :return: None
    """
    if args.product not in ['support', 'help', 'bime', 'explore', 'chat']:
        print('The product name is invalid. Try again.')
        exit()
    if args.article_id and args.user_id:
        kb = KB(args.product)
        kb.update_author(args.article_id, args.user_id)
    else:
        print('Error: Both an article and a user id are required.')


def list_followers(arguments):
    if arguments.product not in ['support', 'help', 'bime', 'explore', 'chat']:
        print('The product name is invalid. Try again.')
        exit()

    hc = HelpCenter(arguments.product)
    if arguments.article:
        hc.list_followers(arguments.item_id, 'article')
    elif arguments.section:
        hc.list_followers(arguments.item_id, 'section')
    elif arguments.post:
        hc.list_followers(arguments.item_id, 'post')
    elif arguments.topic:
        hc.list_followers(arguments.item_id, 'topic')
    else:
        print('Error: You must specify a content type (-a, -s, -p, or -t).')


def list_votes(args):
    if args.product not in ['support', 'help', 'bime', 'explore', 'chat']:
        print('The product name is invalid. Try again.')
        exit()

    hc = HelpCenter(args.product)
    if args.article:
        hc.list_votes(args.item_id, 'article')
    elif args.post:
        hc.list_votes(args.item_id, 'post')
    else:
        print('Error: You must specify a content type (-a or -p).')


def create_post(args):
    if args.product not in ['support', 'help', 'bime', 'explore', 'chat']:
        print('The product name is invalid. Try again.')
        exit()
    c = Community(args.product)
    c.create_post_in_drafts(args.author_id)


def update_post(args):
    if args.product not in ['support', 'help', 'bime', 'explore', 'chat']:
        print('The product name is invalid. Try again.')
        exit()
    c = Community(args.product)
    c.update_post_from_file(args.post_id, args.filename)


parser = argparse.ArgumentParser()
parser.add_argument('--version', action='version', version='1.0.0')
subparsers = parser.add_subparsers()

# python3 hc.py push_staged {product}  {folder_name} --locale {locale} --write
push_staged_parser = subparsers.add_parser('push_staged')
push_staged_parser.add_argument('product', help='support, chat, help, bime, or explore')
push_staged_parser.add_argument('folder_name', help='folder with files in the staging folder')
push_staged_parser.add_argument('--locale', default='en-us', help='locale code')
push_staged_parser.add_argument('--write', '-w', action='store_true', help='push the files to Help Center')
push_staged_parser.set_defaults(func=push_staged)

# python3 hc.py push_dita_html {folder_name} --write
push_dita_html_parser = subparsers.add_parser('push_dita_html')
push_dita_html_parser.add_argument('folder_name', help='folder with transformed files in staging/transformed_files')
push_dita_html_parser.add_argument('--write', '-w', action='store_true', help='push the files to Help Center')
push_dita_html_parser.set_defaults(func=push_dita_html)

# python3 hc.py snapshot {product} -c {id id ...}
snapshot_parser = subparsers.add_parser('snapshot')
snapshot_parser.add_argument('product', help='support, chat, help, bime, or explore')
snapshot_parser.add_argument('--categories', '-c', nargs='*', type=int, help='category ids; if none, uses ini setting')
snapshot_parser.set_defaults(func=take_inventory)

# python3 hc.py change_author {product} {article_id} {new_author_id}
change_author_parser = subparsers.add_parser('change_author')
change_author_parser.add_argument('product', help='support, chat, help, bime, or explore')
change_author_parser.add_argument('article_id', help='HC article id, usually 123456789', type=int)
change_author_parser.add_argument('user_id', help='Zendesk user id, usually 123456789', type=int)
change_author_parser.set_defaults(func=update_author)

# python3 hc.py followers {product} -a -s -p -t {item_id}
followers_parser = subparsers.add_parser('followers')
followers_parser.add_argument('product', help='support, help, chat, bime, or explore')
followers_parser.add_argument('item_id', help='Item id, usually 123456789', type=int)
followers_parser.add_argument('--article', '-a', action='store_true', help='Flag to get article followers')
followers_parser.add_argument('--section', '-s', action='store_true', help='Flag to get section followers')
followers_parser.add_argument('--post', '-p', action='store_true', help='Flag to get post followers')
followers_parser.add_argument('--topic', '-t', action='store_true', help='Flag to get topic followers')
followers_parser.set_defaults(func=list_followers)

# python3 hc.py votes {product} -a -p {item_id}
votes_parser = subparsers.add_parser('votes')
votes_parser.add_argument('product', help='support, chat, help, bime, or explore')
votes_parser.add_argument('item_id', help='article or post id, usually 123456789', type=int)
votes_parser.add_argument('--article', '-a', action='store_true', help='Flag to get article followers')
votes_parser.add_argument('--post', '-p', action='store_true', help='Flag to get post followers')
votes_parser.set_defaults(func=list_votes)

# python3 hc.py create_post {product} {author_id}
create_post_parser = subparsers.add_parser('create_post')
create_post_parser.add_argument('product', help='support, chat, help, bime, or explore')
create_post_parser.add_argument('author_id', help='Zendesk user id, usually 123456789', type=int)
create_post_parser.set_defaults(func=create_post)

# python3 hc.py update_post {product} {post_id} {filename}
update_post_parser = subparsers.add_parser('update_post')
update_post_parser.add_argument('product', help='support, chat, help, bime, or explore')
update_post_parser.add_argument('post_id', help='Zendesk user id, usually 123456789', type=int)
update_post_parser.add_argument('filename', help='HTML file in staging/posts/')
update_post_parser.set_defaults(func=update_post)

if __name__ == '__main__':      # do not comment out - required to call functions
    args = parser.parse_args()
    args.func(args)             # call the default function
