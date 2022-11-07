<a name="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]


<br />
<div align="center">
  <a href="https://github.com/lcram33/compared_copy">
    <img src="images/logo.png" alt="Logo" width="150" height="150">
  </a>

  <h1 align="center">Compared copy</h1>
  
  <h2 align="center">
    A command line program to copy exactly the content of a folder into another one.
  </h2>

  <h3 align="center">
    <br />
    <a href="https://github.com/lcram33/compared_copy/issues">Report Bug</a>
    ·
    <a href="https://github.com/lcram33/compared_copy/issues">Request Feature</a>
  </h3>
</div>


<!-- ABOUT THE PROJECT -->
## About The Project

![Product Name Screen Shot][product-screenshot]

<p align="left">
  A light program to copy exactly the content of a folder into another one.
  It takes into account the existing files, compares and delete the older versions.
  The program works by first creating a full report of what will be done, so you can check which file will be deleted/copied and why.
</p>
<p align="left">
  It applies what is stated in the file, so any change commited after or during the scan will not be considered.
  This program works in Linux based systems (worked with two 5TB HDD on fedora and debian).
</p>
<p align="left">
  It seems like it would not work on Windows. Any fix or change is welcomed !
</p>


### Built With

<a href="https://www.python.org">
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" width=60/>
</a>


<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.


### Prerequisites

* python3 (should come with your favorite distro) and python3-pip
  ```sh
  sudo apt update && sudo apt install python3 python3-pip
  ```
* Following python packages :
  ```sh
  pip3 install colorama
  ```


### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/lcram33/compared_copy.git
   ```
2. cd into the created folder
   ```sh
   cd compared_copy
   ```

3. Start the program
   ```sh
   python3 compared_copy.py
   ```


<!-- USAGE EXAMPLES -->
## Usage

```sh
python3 compared-copy.py /src/path /dest/path
python3 compared-copy.py /src/path /dest/path 1
python3 compared-copy.py
```

The '1' after the dest path tells the program to directly copy after the scan. 

### Ignore files and dirs

To ignore files or dirs, add names or regex on ignore_dirs.list and ignore_files.list (an example is provided for dirs).

### Use md5sum instead of last modification date

If you want to perform md5sum check rather than last modification date (useful on VeraCrypt containers !), just add the files names or regex on md5.list.


<!-- ROADMAP -->
## Roadmap
<h3>
- 🗹 Base program <br>
- ☐ Better console view <br>
- ☐ Graphical interface ? (windowed)
</h3>

See the [open issues](https://github.com/lcram33/compared_copy/issues) for a full list of proposed features (and known issues).


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.


<!-- CONTACT -->
## Contact

✉️ lcram33@pm.me

Project Link: [https://github.com/lcram33/compared_copy](https://github.com/lcram33/compared_copy)


## Credits

<a href="https://www.flaticon.com/free-icons/copy" title="copy icons">Copy icons created by Icongeek26 - Flaticon</a>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/lcram33/compared_copy.svg?style=for-the-badge
[contributors-url]: https://github.com/lcram33/compared_copy/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/lcram33/compared_copy.svg?style=for-the-badge
[forks-url]: https://github.com/lcram33/compared_copy/network/members
[stars-shield]: https://img.shields.io/github/stars/lcram33/compared_copy.svg?style=for-the-badge
[stars-url]: https://github.com/lcram33/compared_copy/stargazers
[issues-shield]: https://img.shields.io/github/issues/lcram33/compared_copy.svg?style=for-the-badge
[issues-url]: https://github.com/lcram33/compared_copy/issues
[license-shield]: https://img.shields.io/github/license/lcram33/compared_copy.svg?style=for-the-badge
[license-url]: https://github.com/lcram33/compared_copy/blob/master/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/marc-lecointre
[product-screenshot]: images/screenshot.png