import argparse

from zep.handoff import Handoff


def create(arguments):
    """
    :param arguments: handoff_name (str), product (str), loader (str)
    :return: void
    """
    if arguments.product not in ['support', 'chat', 'help', 'bime', 'explore']:
        print('The product name is invalid. Try again.')
        exit()
    ho = Handoff(arguments.handoff_name, arguments.product)

    if arguments.loader:
        ho.write_files(arguments.loader)
    else:
        ho.write_files()


def clean(arguments):
    """
    :param arguments: handoff_name (str), product (str), write (bool)
    :return: void
    """
    if arguments.product not in ['support', 'chat', 'help', 'bime', 'explore']:
        print('The product name is invalid. Try again.')
        exit()
    ho = Handoff(arguments.handoff_name, arguments.product)
    ho.strip_comments(arguments.write)


def check_images(arguments):
    """
    :param arguments: handoff_name (str), product (str), exclude (list of ints)
    :return: void
    """
    if arguments.product not in ['support', 'chat', 'help', 'bime', 'explore']:
        print('The product name is invalid. Try again.')
        exit()
    ho = Handoff(arguments.handoff_name, arguments.product)

    if arguments.exclude:
        ho.check_images(arguments.exclude)    # [203664236, 203664256, 203664246, 203664226]
    else:
        ho.check_images()


def copy_images(arguments):
    """
    :param arguments: handoff_name (str),  product (str), months (int), exclude (list of ints)
    :return: void
    """
    if arguments.product not in ['support', 'chat', 'help', 'bime', 'explore']:
        print('The product name is invalid. Try again.')
        exit()
    ho = Handoff(arguments.handoff_name, arguments.product)

    if arguments.months:
        arguments.months = int(arguments.months)      # function takes an int
        ho.copy_images(arguments.months, arguments.exclude)
    else:
        ho.copy_images(exclude=arguments.exclude)


def package(arguments):
    """
    :param arguments: handoff_name, product (str)
    :return: void
    """
    if arguments.product not in ['support', 'chat', 'help', 'bime', 'explore']:
        print('The product name is invalid. Try again.')
        exit()
    ho = Handoff(arguments.handoff_name, arguments.product)
    ho.zip_files()


def upload(arguments):
    """
    :param arguments: handoff_name, product (str)
    :return: void
    """
    if arguments.product not in ['support', 'chat', 'help', 'bime', 'explore']:
        print('The product name is invalid. Try again.')
        exit()
    ho = Handoff(arguments.handoff_name, arguments.product)
    ho.upload_handoff()


def register(arguments):
    """
    :param arguments: handoff_name (str), product (str), articles (bool), images (bool), locales (list), write (bool)
    :return: void
    """

    if arguments.product not in ['support', 'chat', 'help', 'bime', 'explore']:
        print('The product name is invalid. Try again.')
        exit()
    ho = Handoff(arguments.handoff_name, arguments.product)

    if arguments.articles or arguments.images:
        if arguments.articles:
            ho.update_article_registry(arguments.locales, arguments.write)
        if arguments.images:
            ho.update_image_registry(arguments.locales, arguments.write)
    else:
        ho.update_article_registry(arguments.locales, arguments.write)
        ho.update_image_registry(arguments.locales, arguments.write)


def relink(arguments):
    """
    :param arguments: handoff_name (str), product (str), articles (bool), images (bool), locales (list), write (bool)
    :return: void
    """
    if arguments.product not in ['support', 'chat', 'help', 'bime', 'explore']:
        print('The product name is invalid. Try again.')
        exit()
    ho = Handoff(arguments.handoff_name, arguments.product)

    if arguments.hrefs or arguments.srcs:
        if arguments.hrefs:
            ho.update_hrefs(arguments.locales, arguments.write)
        if arguments.srcs:
            ho.update_srcs(arguments.locales, arguments.write)
    else:
        ho.update_hrefs(arguments.locales, arguments.write)
        ho.update_srcs(arguments.locales, arguments.write)


def publish(arguments):
    """
    :param arguments: handoff_name (str), product (str), locales (list), write (bool)
    :return: void
    """
    if arguments.product not in ['support', 'chat', 'help', 'bime', 'explore']:
        print('The product name is invalid. Try again.')
        exit()
    ho = Handoff(arguments.handoff_name, arguments.product)
    ho.publish_handoff(arguments.locales, arguments.write)


parser = argparse.ArgumentParser()
parser.add_argument('--version', action='version', version='1.0.0')
subparsers = parser.add_subparsers()

# python3 ho.py create {handoff_name} {product} --loader={filename}
create_parser = subparsers.add_parser('create')
create_parser.add_argument('handoff_name', help='handoff name, usually yyyy-mm-dd')
create_parser.add_argument('product', help='support, chat, bime, help, or explore')
create_parser.add_argument('--loader',
                           help='custom name of file with ids of articles to download (default = _loader.txt)')
create_parser.set_defaults(func=create)

# python3 ho.py clean {handoff_name} {product} --write
clean_parser = subparsers.add_parser('clean')
clean_parser.add_argument('handoff_name', help='handoff name, usually yyyy-mm-dd')
clean_parser.add_argument('product', help='support, chat, bime, help, or explore')
clean_parser.add_argument('--write', '-w', action='store_true', help='write changes to file')
clean_parser.set_defaults(func=clean)

# python3 ho.py check_images {handoff_name} {product} --exclude {id id ...}
check_images_parser = subparsers.add_parser('check_images')
check_images_parser.add_argument('handoff_name', help='handoff name, usually yyyy-mm-dd')
check_images_parser.add_argument('product', help='support, chat, bime, help, or explore')
check_images_parser.add_argument('--exclude', nargs='*', type=int,
                                 help='ids of articles that use en-us images in loc versions')
check_images_parser.set_defaults(func=check_images)

# python3 ho.py copy_images {handoff_name} {product} --months={int} --exclude {id id ...}
copy_images_parser = subparsers.add_parser('copy_images')
copy_images_parser.add_argument('handoff_name', help='handoff name, usually yyyy-mm-dd')
copy_images_parser.add_argument('product', help='support, chat, bime, help, or explore')
copy_images_parser.add_argument('--months', help='number of months to go back when en-us images were last updated')
copy_images_parser.add_argument('--exclude', nargs='*', type=int,
                                help='ids of articles that use en-us images in loc versions')
copy_images_parser.set_defaults(func=copy_images)

# python3 ho.py package {handoff_name} {product}
package_parser = subparsers.add_parser('package')
package_parser.add_argument('handoff_name', help='handoff name, usually yyyy-mm-dd')
package_parser.add_argument('product', help='support, chat, bime, help, or explore')
package_parser.set_defaults(func=package)

# python3 ho.py upload {handoff_name} {product}
upload_parser = subparsers.add_parser('upload')
upload_parser.add_argument('handoff_name', help='handoff name, usually yyyy-mm-dd')
upload_parser.add_argument('product', help='support, chat, bime, help, or explore')
upload_parser.set_defaults(func=upload)

# python3 ho.py register {handoff_name} {product} --articles --images --locales --write
register_parser = subparsers.add_parser('register')
register_parser.add_argument('handoff_name', help='handoff name, usually yyyy-mm-dd')
register_parser.add_argument('product', help='support, chat, bime, help, or explore')
register_parser.add_argument('--articles', action='store_true', help='add only articles to registry')
register_parser.add_argument('--images', action='store_true', help='add only images to registry')
register_parser.add_argument('--locales', nargs='*', help='specific locales; if none specified, uses all')
register_parser.add_argument('--write', '-w', action='store_true', help='write changes to file')
register_parser.set_defaults(func=register)

# python3 ho.py relink {handoff_name} {product} --hrefs --srcs --locales {loc loc ...} --write
relink_parser = subparsers.add_parser('relink')
relink_parser.add_argument('handoff_name', help='handoff name, usually yyyy-mm-dd')
relink_parser.add_argument('product', help='support, chat, bime, help, or explore')
relink_parser.add_argument('--hrefs', action='store_true', help='update article links')
relink_parser.add_argument('--srcs', action='store_true', help='update image links')
relink_parser.add_argument('--locales', nargs='*', help='specific locales; if none specified, uses all')
relink_parser.add_argument('--write', '-w', action='store_true', help='write changes to file')
relink_parser.set_defaults(func=relink)

# python3 ho.py publish {handoff_name} {product} --locales {loc loc ...} --write
publish_parser = subparsers.add_parser('publish')
publish_parser.add_argument('handoff_name', help='handoff name, usually yyyy-mm-dd')
publish_parser.add_argument('product', help='support, chat, bime, help, or explore')
publish_parser.add_argument('--locales', nargs='*', help='specific locales; if none specified, uses all')
publish_parser.add_argument('--write', '-w', action='store_true', help='publish the files to Help Center')
publish_parser.set_defaults(func=publish)

if __name__ == '__main__':      # do NOT comment out - required to call functions
    args = parser.parse_args()
    args.func(args)             # call the default function
