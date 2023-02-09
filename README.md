# CSVMerge GTK

This is a Python GTK application built with PyGObject for previewing and merging CSV files obtained with the [ENLIGHTEN Spectroscopy Software](https://wasatchphotonics.com/product-category/software/) from [Wasatch Photonics](https://wasatchphotonics.com/). The application has been tested and works on Fedora 37 and Ubuntu 22.04.

> Are you using Windows? Check out the sibling application [Spectra CSV Merger](https://myweb.uoi.gr/nkourkou/index.php?id=software).

## Installation

`pip` is required for the installation of the package, wich also handles its dependencies (`pygobject` and `matplotlib`). It can be installed wth the following command (depending on the distribution):

- For Ubuntu:

      sudo apt install python3-pip

- For Fedora:

      sudo dnf install python3-pip

After installing `pip`, clone the repository:

    git clone https://github.com/lepa22/csvmerge_gtk.git

Then from within the package directory run the `install.sh` file:

    ./install.sh

The `install.sh` script also adds a `.desktop` file so that the application can be launched from the application menu.

## Contributing

Feel free to contribute to the project by submitting pull requests or by reporting issues.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.