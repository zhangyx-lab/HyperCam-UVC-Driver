FLAGS   ?= -p
EXEC    ?= python3 ./main.py
EXEC    += $(FLAGS)
ACTIONS := calibrate capture preview

all: tmp $(ACTIONS)
 
CAPTURE_CONF:=led=$${i};pwm=2;exp=1;stack=1;out=tmp/cap_$${i}.png
capture:
	$(info $(CAPTURE_CONF))
	@bash -c 'for i in {1..8}; do cat var/cal_led_$$i.txt | tr "\n" ";"; echo; done' \
	| $(EXEC)

PREVIEW_CONF:=out=tmp/preview.png
preview:
	@bash -c 'for i in {1..99}; do echo "$(PREVIEW_CONF)"; done' \
	| $(EXEC)

CALIB_CONF:=led=$${i};stack=2;out=tmp/calibrate_$${i}.png
calibrate:
	@bash -c 'for i in {1..8}; do echo "$(CALIB_CONF)"; done' \
	| $(EXEC)

tmp var:
	mkdir -p $@

clean:
	rm -rf tmp

.PHONY: $(ACTIONS) clean
