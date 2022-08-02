from loader import bot
import commands


def main():
    bot.polling(non_stop=True, interval=0)


if __name__ == '__main__':
    main()