
import nose

if __name__ == '__main__':
    args = [
        '--verbosity=3',
        '--nocapture',
        '--with-doctest',
    ]

    nose.main(argv=args)
