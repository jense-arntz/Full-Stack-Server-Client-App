  //initialize the javascript
  $('#camera').addClass("selected");
  get_setting();
  // <-------------------------Get the IP Settings from Camera---------------------->
  function get_setting() {
     $.getJSON('/api/control/summary', function (data) {
        $.each(data, function (key, item) {
           $('#form-camera')
                 .find('[name="jpeg-compression-settings"]').val(item.jpeg_compression_settings).end()
                 .find('[name="white-balance"]').val(item.white_balance).end()
                 .find('[name="f-number"]').val(item.f_number).end()
                 .find('[name="exposure-metering-mode"]').val(item.exposure_metering_mode).end()
                 .find('[name="iso"]').val(item.iso).end()
                 .find('[name="exposure-compensation"]').val(item.exposure_compensation).end()
                 .find('[name="still-capture-mode"]').val(item.still_capture_mode).end()
                 .find('[name="auto-iso"]').val(item.auto_iso).end()
                 .find('[name="long-exposure-noise-reduction"]').val(item.long_exposure_noise_reduction).end()
                 .find('[name="autofocus-mode"]').val(item.autofocus_mode).end()
                 .find('[name="af-assist-lamp"]').val(item.af_assist_lamp).end()
                 .find('[name="auto-iso-hight-limit"]').val(item.auto_iso).end()
                 .find('[name="manufactuer"]').val(item.manufacturer).end()
                 .find('[name="model"]').val(item.model).end()
                 .find('[name="version"]').val(item.version).end()
                 .find('[name="serial-number"]').val(item.serial_number).end()
                 .find('[name="free-space-sd-card"]').val(item.free_space_sd_card).end()
                 .find('[name="current-focal-length"]').val(item.current_focal_length).end()
                 .find('[name="exposure-time"]').val(item.exposure_time).end()
                 .find('[name="exposure-program-mode"]').val(item.exposure_program_mode).end()
                 .find('[name="shutter-count"]').val(item.shutter_count).end();
        });
     });
  }

  $('#reset').click(function () {
     $.ajax({
        type: "GET",
        dataType: "text",
        url: "/api/camera/reset",
        success: function (data) {
           alert(data);
           get_setting();
        }
     });
  });
