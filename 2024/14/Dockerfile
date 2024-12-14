FROM rust

RUN mkdir /rust-iter
WORKDIR /usr/src/

RUN cargo new aoc14  && ls -la
WORKDIR /usr/src/aoc14
RUN cargo add regex  && ls -la
COPY aoc14.rs src/main.rs
RUN cargo install --path .
WORKDIR /
COPY input.txt /

CMD ["/usr/local/cargo/bin/aoc14"]

