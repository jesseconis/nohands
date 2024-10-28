# Maintainer: Jesse Conis me@jesseconis.io
pkgname=nohands
pkgver=0.1.0
pkgrel=1
pkgdesc="dev automation utilities"
arch=('any')
url="https://github.com/jesseconis/nohands"
license=('MIT')
depends=(
    'python'
    'python-pygit2'
    'python-watchfiles'
    'python-typer'
    'python-tomli'
)
makedepends=(
    'git'
    'python-build' 
    'python-installer' 
    'python-wheel'
    'python-setuptools'
)
source=("$pkgname::git+file://${PWD}")
sha256sums=('SKIP')

build() {
    echo "Build.."
    echo "cd $srcdir/$pkgdir"
    cd "$srcdir/$pkgname"
    # Copy pyproject.toml to where we're building
    python -m build --wheel --no-isolation
}

package() {
    cd "$srcdir/$pkgname"
    python -m installer --destdir="$pkgdir" dist/*.whl

    # Install systemd service file
    install -Dm644 "nohands.service" \
        "$pkgdir/usr/lib/systemd/system/nohands.service"

    # Install default config file
    install -Dm644 "config/nohands.conf.example" \
        "$pkgdir/etc/nohands/nohands.conf.example"

    # Install license
    install -Dm644 "LICENSE" \
        "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}

